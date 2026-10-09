"""SG28: CI-only bounded subprocess termination proof, not production API."""
import time

import pytest

from app.services.interruptible import ComputationTimedOut, run_bounded


def _add(a: int, b: int) -> int:
    return a + b


def _bounded_wait() -> None:
    time.sleep(2)


def test_isolated_computation_returns_result() -> None:
    assert run_bounded(_add, 2, 3, timeout_seconds=5) == 5


def test_timeout_terminates_isolated_process_and_recovers() -> None:
    started = time.monotonic()
    with pytest.raises(ComputationTimedOut):
        run_bounded(_bounded_wait, timeout_seconds=0.2)
    assert time.monotonic() - started < 3
    assert run_bounded(_add, 2, 3, timeout_seconds=5) == 5


def test_invalid_timeout_rejected() -> None:
    with pytest.raises(ValueError):
        run_bounded(_add, 2, 3, timeout_seconds=0)


def _real_sympy_evaluation() -> str:
    """Run actual SymPy in an isolated child, not a fabricated arithmetic stub."""
    import sympy
    x = sympy.Symbol("x")
    return str(sympy.diff(x**3 + 2*x, x))


def test_real_sympy_operation_executes_in_isolated_process() -> None:
    assert run_bounded(_real_sympy_evaluation, timeout_seconds=5) == "3*x**2 + 2"


def test_real_sympy_operation_recovers_after_killed_process() -> None:
    with pytest.raises(ComputationTimedOut):
        run_bounded(_bounded_wait, timeout_seconds=0.2)
    assert run_bounded(_real_sympy_evaluation, timeout_seconds=5) == "3*x**2 + 2"
