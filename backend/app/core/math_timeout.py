"""Hard wall-clock budget for expensive symbolic math operations.

The outer API call is isolated in a fresh spawned process so timed-out
SymPy work can be terminated without inheriting locks from Uvicorn or
other runtime threads. Nested guarded calls inside that child use SIGALRM
instead of trying to create another process.
"""

from __future__ import annotations

import multiprocessing
import signal
import threading
from typing import Callable, TypeVar

from app.core.config import get_settings

T = TypeVar("T")


def _process_entry(sender, func, args: tuple, kwargs: dict) -> None:
    try:
        result = func(*args, **kwargs)
        sender.send(("ok", result))
    except BaseException as exc:
        try:
            sender.send(("err", exc))
        except BaseException:
            sender.send(("err_text", (type(exc).__name__, str(exc))))
    finally:
        sender.close()


def _run_in_spawned_process(
    func: Callable[..., T],
    args: tuple,
    kwargs: dict,
    budget: float,
) -> T:
    ctx = multiprocessing.get_context("spawn")
    receiver, sender = ctx.Pipe(duplex=False)
    process = ctx.Process(
        target=_process_entry,
        args=(sender, func, args, kwargs),
        daemon=False,
    )
    process.start()
    sender.close()
    try:
        if receiver.poll(budget):
            status, payload = receiver.recv()
            process.join(timeout=0.25)
            if process.is_alive():
                process.terminate()
                process.join(timeout=0.25)
            if status == "ok":
                return payload
            if status == "err":
                raise payload
            name, message = payload
            raise RuntimeError(f"{name}: {message}")

        process.terminate()
        process.join(timeout=0.5)
        if process.is_alive() and hasattr(process, "kill"):
            process.kill()
            process.join(timeout=0.5)
        raise TimeoutError(f"Operación matemática excedió {budget:g}s.")
    finally:
        receiver.close()
        if process.is_alive():
            process.terminate()
            process.join(timeout=0.25)


def _run_with_signal(
    func: Callable[..., T],
    args: tuple,
    kwargs: dict,
    budget: float,
) -> T:
    if (
        threading.current_thread() is not threading.main_thread()
        or not hasattr(signal, "SIGALRM")
        or not hasattr(signal, "setitimer")
    ):
        return func(*args, **kwargs)

    old_handler = signal.getsignal(signal.SIGALRM)
    old_timer = signal.getitimer(signal.ITIMER_REAL)

    def _raise_timeout(_signum, _frame):
        raise TimeoutError(f"Operación matemática excedió {budget:g}s.")

    signal.signal(signal.SIGALRM, _raise_timeout)
    signal.setitimer(signal.ITIMER_REAL, budget)
    try:
        return func(*args, **kwargs)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old_handler)
        if old_timer != (0.0, 0.0):
            signal.setitimer(signal.ITIMER_REAL, *old_timer)


def run_math_operation(
    func: Callable[..., T],
    *args,
    timeout_s: float | None = None,
    **kwargs,
) -> T:
    budget = get_settings().math_timeout_seconds if timeout_s is None else float(timeout_s)
    if budget <= 0:
        return func(*args, **kwargs)

    # We are already inside the isolated worker. Do not recursively spawn;
    # use an interruptible local alarm for nested verification/simplify calls.
    if multiprocessing.current_process().name != "MainProcess":
        return _run_with_signal(func, args, kwargs, budget)

    if "spawn" in multiprocessing.get_all_start_methods():
        return _run_in_spawned_process(func, args, kwargs, budget)

    return _run_with_signal(func, args, kwargs, budget)
