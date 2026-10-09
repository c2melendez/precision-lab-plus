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
