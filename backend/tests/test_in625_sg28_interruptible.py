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


def _sympy_after_gate(ready, release) -> str:
    """Perform genuine SymPy work only after parent confirms child is running."""
    ready.set()
    if not release.wait(timeout=3):
        raise RuntimeError("Test gate was never opened")
    return _real_sympy_evaluation()


def test_running_sympy_worker_is_terminated_before_evaluation_and_recovers() -> None:
    """Terminate a live child with a gated SymPy operation, not only a sleep stub."""
    import multiprocessing as mp

    ctx = mp.get_context("spawn")
    ready = ctx.Event()
    release = ctx.Event()
    # The process is already alive and blocked at a documented deterministic
    # gate. A short timeout must terminate it without starting SymPy compute.
    with pytest.raises(ComputationTimedOut):
        run_bounded(_sympy_after_gate, ready, release, timeout_seconds=0.3)
    assert ready.is_set(), "The isolated SymPy child never reached its active gate"
    assert run_bounded(_real_sympy_evaluation, timeout_seconds=5) == "3*x**2 + 2"
