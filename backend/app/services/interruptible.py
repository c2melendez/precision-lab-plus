"""Isolated SG28 prototype: bounded, killable child-process execution.

Not connected to public API routes. A frontend HTTP AbortController is NOT a
server-side cancellation mechanism. This primitive is intended for isolated CI
evaluation before any production integration.
"""
from __future__ import annotations

import multiprocessing as mp
import os
import json
import time
from typing import Any, Callable


def _record_sg28_event(event: str, pid: int | None) -> None:
    path = os.getenv('SG28_CI_EVENT_FILE')
    if path and os.getenv('SG28_CI_OBSERVE', '0') == '1':
        with open(path, 'a', encoding='utf-8') as log:
            log.write(json.dumps({'event': event, 'pid': pid, 'time': time.monotonic()}) + '\n')


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
        # SG28 optional POSIX CPU budget, limited to this spawned child.
        # Opt-in only; independent of the existing wall-clock cancellation.
        cpu_budget = os.getenv("SG28_ISOLATED_CPU_SECONDS")
        if cpu_budget and os.name == "posix":
            import resource
            seconds = int(cpu_budget)
            if not 1 <= seconds <= 8:
                raise ValueError("SG28 CPU budget must be 1..8 seconds")
            resource.setrlimit(resource.RLIMIT_CPU, (seconds, seconds + 1))
        # Virtual-address-space ceiling is likewise opt-in and child-only.
        memory_mb = os.getenv("SG28_ISOLATED_MEMORY_MB")
        if memory_mb and os.name == "posix":
            import resource
            megabytes = int(memory_mb)
            if not 256 <= megabytes <= 4096:
                raise ValueError("SG28 memory budget must be 256..4096 MiB")
            ceiling = megabytes * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (ceiling, ceiling))
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
            _record_sg28_event('start', process.pid)
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
            # POSIX CPU-budget exhaustion terminates the worker by SIGXCPU.
            process.join(timeout=0.2)
            if os.name == "posix" and os.getenv("SG28_ISOLATED_CPU_SECONDS"):
                import signal
                if process.exitcode == -signal.SIGXCPU:
                    raise ComputationTimedOut("Isolated CPU budget exceeded") from exc
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
            _record_sg28_event('finish', pid)
