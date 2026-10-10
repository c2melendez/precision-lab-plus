"""SG28 experimental ASGI request-to-isolated-process cancellation bridge.

Not wired into production routes. The blocking process coordinator runs in an
executor thread, while the event loop checks for ASGI client disconnects.
"""
from __future__ import annotations

import asyncio
import threading
from typing import Any, Callable

from starlette.requests import Request

from app.services.interruptible import ComputationCancelled, run_bounded


async def run_for_request(
    request: Request,
    operation: Callable[..., Any],
    *args: Any,
    timeout_seconds: float = 3.0,
) -> Any:
    """Cancel isolated work on client disconnect or coroutine cancellation."""
    cancelled = threading.Event()
    task = asyncio.create_task(
        asyncio.to_thread(
            run_bounded, operation, *args,
            timeout_seconds=timeout_seconds,
            cancel_event=cancelled,
        )
    )
    try:
        while not task.done():
            if await request.is_disconnected():
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
