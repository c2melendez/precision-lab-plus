"""Isolated SG28 prototype: bounded, killable child-process execution.

Not connected to public API routes. A frontend HTTP AbortController is NOT a
server-side cancellation mechanism. This primitive is intended for isolated CI
evaluation before any production integration.
"""
from __future__ import annotations

import multiprocessing as mp
import os
import time
from typing import Any, Callable


class ComputationTimedOut(TimeoutError):
    """The isolated computation exceeded its wall-clock allowance."""


class ComputationCancelled(RuntimeError):
    """The caller requested interruption of the isolated child."""


class ComputationFailed(RuntimeError):
    """The isolated computation failed, with its original error type retained."""

    def __init__(self, message: str, error_type: str | None = None):
        super().__init__(message)
        self.error_type = error_type


def _child_main(send: Any, operation: Callable[..., Any], args: tuple[Any, ...]) -> None:
    try:
        send.send(("ok", operation(*args)))
    except Exception as exc:
        send.send(("error", (type(exc).__name__, str(exc))))
    finally:
        send.close()


def run_bounded(
    operation: Callable[..., Any], *args: Any, timeout_seconds: float = 2.0,
    cancel_event: Any = None,
) -> Any:
    """Run a picklable operation in a distinct process and stop it on timeout.

    Prototype limitations: only small, picklable inputs/outputs; no routing,
    request-disconnect propagation, quotas or production worker pool.
    """
    if not 0 < timeout_seconds <= 10:
        raise ValueError("timeout_seconds must be between 0 and 10")
    ctx = mp.get_context("spawn")
    receive, send = ctx.Pipe(duplex=False)
    process = ctx.Process(target=_child_main, args=(send, operation, args), daemon=True)
    try:
        process.start()
        if os.getenv('SG28_CI_OBSERVE', '0') == '1':
            print(f'SG28_CHILD_START {process.pid}', flush=True)
        send.close()
        deadline = time.monotonic() + timeout_seconds
        while True:
            if cancel_event is not None and cancel_event.is_set():
                raise ComputationCancelled("Caller cancelled isolated computation")
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ComputationTimedOut("Computation exceeded isolated time limit")
            if receive.poll(min(remaining, 0.05)):
                break
        if cancel_event is not None and cancel_event.is_set():
            raise ComputationCancelled("Caller cancelled isolated computation")
        try:
            status, payload = receive.recv()
        except EOFError as exc:
            raise ComputationFailed("Child process exited without a response") from exc
        if status != "ok":
            if isinstance(payload, tuple) and len(payload) == 2:
                error_type, message = payload
                raise ComputationFailed(f"{error_type}: {message}", str(error_type))
            raise ComputationFailed(str(payload))
        return payload
    finally:
        receive.close()
        send.close()
        if process.is_alive():
            process.terminate()
            process.join(timeout=1)
            if process.is_alive():
                process.kill()
                process.join(timeout=1)
        pid = process.pid
        process.close()
        if os.getenv('SG28_CI_OBSERVE', '0') == '1':
            print(f'SG28_CHILD_FINISH {pid}', flush=True)
