import multiprocessing
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from app.core.math_timeout import run_math_operation


def test_math_timeout_allows_fast_operation():
    assert run_math_operation(lambda: 42, timeout_s=0.2) == 42


def test_math_timeout_propagates_service_exception():
    def fail():
        raise ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        run_math_operation(fail, timeout_s=0.2)


@pytest.mark.skipif(
    "fork" not in multiprocessing.get_all_start_methods(),
    reason="Hard timeout isolation requires fork.",
)
def test_math_timeout_interrupts_cpu_bound_operation():
    started = time.perf_counter()

    def slow():
        while True:
            pass

    with pytest.raises(TimeoutError):
        run_math_operation(slow, timeout_s=0.05)

    assert time.perf_counter() - started < 1.0


@pytest.mark.skipif(
    "fork" not in multiprocessing.get_all_start_methods(),
    reason="Hard timeout isolation requires fork.",
)
def test_math_timeout_also_works_when_called_from_worker_thread():
    def invoke():
        def slow():
            while True:
                pass
        with pytest.raises(TimeoutError):
            run_math_operation(slow, timeout_s=0.05)
        return "done"

    with ThreadPoolExecutor(max_workers=1) as executor:
        assert executor.submit(invoke).result(timeout=1.0) == "done"
