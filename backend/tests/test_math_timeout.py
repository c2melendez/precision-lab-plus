import signal
import threading
import time

import pytest

from app.core.math_timeout import run_math_operation


def test_math_timeout_allows_fast_operation():
    assert run_math_operation(lambda: 42, timeout_s=0.2) == 42


@pytest.mark.skipif(
    threading.current_thread() is not threading.main_thread()
    or not hasattr(signal, "SIGALRM")
    or not hasattr(signal, "setitimer"),
    reason="Interruptible timeout requires Unix main-thread signals.",
)
def test_math_timeout_interrupts_cpu_bound_operation():
    started = time.perf_counter()

    def slow():
        while True:
            pass

    with pytest.raises(TimeoutError):
        run_math_operation(slow, timeout_s=0.05)

    assert time.perf_counter() - started < 1.0
