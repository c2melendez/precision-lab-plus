"""SG28 experimental ASGI request-to-isolated-process cancellation bridge.

Not wired into production routes. The blocking process coordinator runs in an
executor thread, while the event loop checks for ASGI client disconnects.
"""
from __future__ import annotations

import asyncio
import os
import threading
from typing import Any, Callable

from starlette.requests import Request

from app.services.interruptible import ComputationCancelled, run_bounded

# Per Python worker-process admission: fail closed when the budget is full.
_MAX_ISOLATED_REQUESTS = max(1, min(int(os.getenv("SG28_MAX_ISOLATED_REQUESTS", "2")), 16))
_ADMISSION = threading.BoundedSemaphore(_MAX_ISOLATED_REQUESTS)


class IsolationCapacityExceeded(RuntimeError):
    """The bounded isolated-worker pool has no available admission slot."""


async def run_for_request(
    request: Request,
    operation: Callable[..., Any],
    *args: Any,
    timeout_seconds: float = 3.0,
) -> Any:
    """Cancel isolated work on client disconnect or coroutine cancellation."""
    if not _ADMISSION.acquire(blocking=False):
        raise IsolationCapacityExceeded("Isolated evaluation capacity reached")
    cancelled = threading.Event()
    try:
        task = asyncio.create_task(
        asyncio.to_thread(
            run_bounded, operation, *args,
            timeout_seconds=timeout_seconds,
            cancel_event=cancelled,
        )
        )
    except BaseException:
        _ADMISSION.release()
        raise
    try:
        while not task.done():
            # The outer ASGI tracker also sees disconnects consumed by HTTP middleware.
            disconnect_event = getattr(request, "scope", {}).get("sg28_http_disconnected")
            if (disconnect_event is not None and disconnect_event.is_set()) or await request.is_disconnected():
                cancelled.set()
                # Do not return before process coordinator performs cleanup.
                try:
                    await asyncio.shield(task)
                except ComputationCancelled:
                    pass
                raise ComputationCancelled("HTTP client disconnected")
            await asyncio.sleep(0.025)
        return await task
    except asyncio.CancelledError:
        cancelled.set()
        try:
            await asyncio.shield(task)
        except (ComputationCancelled, asyncio.CancelledError):
            pass
        raise
    finally:
        cancelled.set()
        # A cancelled coroutine must not release capacity while its thread still runs.
        if task.done():
            _ADMISSION.release()
        else:
            task.add_done_callback(lambda _: _ADMISSION.release())
