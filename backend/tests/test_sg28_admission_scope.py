"""SG28 local admission regression and independent-pool characterization.

These are unit tests only: they do not establish multi-process or fleet quotas.
"""
import threading

import pytest

from app.services import request_cancellation as cancellation


def test_sg28_local_admission_is_bounded_and_recovers(monkeypatch):
    monkeypatch.setattr(cancellation, "_ADMISSION", threading.BoundedSemaphore(1))
    with cancellation.request_admission_lease():
        with pytest.raises(cancellation.IsolationCapacityExceeded):
            with cancellation.request_admission_lease():
                pytest.fail("Second local admission should be rejected")
    with cancellation.request_admission_lease():
        pass


def test_sg28_distinct_local_pools_can_each_admit_one():
    first = threading.BoundedSemaphore(1)
    second = threading.BoundedSemaphore(1)
    assert first.acquire(blocking=False)
    assert second.acquire(blocking=False)
    try:
        assert not first.acquire(blocking=False)
        assert not second.acquire(blocking=False)
    finally:
        first.release()
        second.release()
    # Independent pools are not a global budget. This test does NOT launch
    # multiple interpreters, exercise HTTP, or validate deployment topology.
