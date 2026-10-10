"""SG28 regression for admission scope.

This test intentionally characterizes the existing *local* admission policy;
it is not evidence of fleet-wide enforcement.
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


def test_sg28_distinct_admission_pools_do_not_share_a_quota(monkeypatch):
    first = threading.BoundedSemaphore(1)
    second = threading.BoundedSemaphore(1)
    monkeypatch.setattr(cancellation, "_ADMISSION", first)
    with cancellation.request_admission_lease():
        monkeypatch.setattr(cancellation, "_ADMISSION", second)
        with cancellation.request_admission_lease():
            pass
    # Two distinct pools each admitted work: this is a model of process
    # isolation, NOT an actual multiprocess or distributed integration test.
