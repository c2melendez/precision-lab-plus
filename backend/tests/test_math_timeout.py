import multiprocessing
import time

import pytest

from app.core.math_timeout import run_math_operation


def _return_42():
    return 42


def _raise_value_error():
    raise ValueError("boom")


def _spin_forever():
    while True:
        pass


def test_math_timeout_allows_fast_spawn_safe_operation():
    assert run_math_operation(_return_42, timeout_s=0.5) == 42


def test_math_timeout_propagates_service_exception():
    with pytest.raises(ValueError, match="boom"):
        run_math_operation(_raise_value_error, timeout_s=0.5)


@pytest.mark.skipif(
    "spawn" not in multiprocessing.get_all_start_methods(),
    reason="Hard timeout isolation requires spawn.",
)
def test_math_timeout_hard_kills_isolated_cpu_bound_operation():
    started = time.perf_counter()
    with pytest.raises(TimeoutError):
        run_math_operation(_spin_forever, timeout_s=0.1)
    # The first forkserver startup may preload SymPy on a cold CI runner.
    # The operation budget is still 0.1s; this bound only covers process
    # bootstrap/teardown overhead and guards against a leaked child.
    assert time.perf_counter() - started < 6.0


def test_math_timeout_supports_unpicklable_lambda_with_signal_fallback():
    assert run_math_operation(lambda: 7, timeout_s=0.2) == 7
