"""Interruptible wall-clock budget for expensive symbolic math operations.

On Linux/Unix (Render and GitHub Actions), SIGALRM interrupts the actual
Python/SymPy call instead of merely abandoning the HTTP request. This avoids
leaving a CPU-bound symbolic calculation running after the frontend timeout.
"""

from __future__ import annotations

import signal
import threading
from typing import Callable, TypeVar

from app.core.config import get_settings

T = TypeVar("T")


def run_math_operation(
    func: Callable[..., T],
    *args,
    timeout_s: float | None = None,
    **kwargs,
) -> T:
    budget = get_settings().math_timeout_seconds if timeout_s is None else float(timeout_s)
    if budget <= 0:
        return func(*args, **kwargs)

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
