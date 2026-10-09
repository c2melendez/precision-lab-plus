"""Isolated SG28 prototype: bounded, killable child-process execution.

Not connected to public API routes. A frontend HTTP AbortController is NOT a
server-side cancellation mechanism. This primitive is intended for isolated CI
evaluation before any production integration.
"""
from __future__ import annotations

import multiprocessing as mp
from typing import Any, Callable


class ComputationTimedOut(TimeoutError):
    """The isolated computation exceeded its wall-clock allowance."""


class ComputationFailed(RuntimeError):
    """The isolated computation exited without returning a result."""


def _child_main(send: Any, operation: Callable[..., Any], args: tuple[Any, ...]) -> None:
    try:
        send.send(("ok", operation(*args)))
    except Exception as exc:
        send.send(("error", f"{type(exc).__name__}: {exc}"))
    finally:
        send.close()


def run_bounded(operation: Callable[..., Any], *args: Any, timeout_seconds: float = 2.0) -> Any:
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
        send.close()
        if not receive.poll(timeout_seconds):
            process.terminate()
            process.join(timeout=1)
            if process.is_alive():
                process.kill()
                process.join(timeout=1)
            raise ComputationTimedOut("Computation exceeded isolated time limit")
        try:
            status, payload = receive.recv()
        except EOFError as exc:
            raise ComputationFailed("Child process exited without a response") from exc
        if status != "ok":
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
        process.close()
