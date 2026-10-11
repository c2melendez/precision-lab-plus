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


def test_sg28_local_admission_released_after_exception(monkeypatch):
    """An exception inside a reserved request must not permanently exhaust its slot."""
    monkeypatch.setattr(cancellation, "_ADMISSION", threading.BoundedSemaphore(1))
    with pytest.raises(RuntimeError, match="synthetic request failure"):
        with cancellation.request_admission_lease():
            with pytest.raises(cancellation.IsolationCapacityExceeded):
                with cancellation.request_admission_lease():
                    pytest.fail("A second request must not acquire the occupied slot")
            raise RuntimeError("synthetic request failure")
    # A failed request has fully relinquished its slot.
    with cancellation.request_admission_lease():
        pass


def test_sg28_local_admission_released_after_async_task_cancellation(monkeypatch):
    """Cancellation while holding a lease must free the one local slot."""
    import asyncio

    monkeypatch.setattr(cancellation, "_ADMISSION", threading.BoundedSemaphore(1))

    async def scenario():
        entered = asyncio.Event()

        async def reserved():
            with cancellation.request_admission_lease():
                entered.set()
                await asyncio.Event().wait()

        task = asyncio.create_task(reserved())
        try:
            await asyncio.wait_for(entered.wait(), timeout=2)
            with pytest.raises(cancellation.IsolationCapacityExceeded):
                with cancellation.request_admission_lease():
                    pytest.fail("Busy slot unexpectedly admitted another request")
        finally:
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await asyncio.wait_for(task, timeout=2)

        with cancellation.request_admission_lease():
            pass

    asyncio.run(scenario())


def test_sg28_local_admission_released_after_nested_exception_group(monkeypatch):
    """Cleanup must occur even when multiple request phases fail together."""
    monkeypatch.setattr(cancellation, "_ADMISSION", threading.BoundedSemaphore(1))
    with pytest.raises(ExceptionGroup) as captured:
        with cancellation.request_admission_lease():
            raise ExceptionGroup("phase failures", [
                ValueError("evaluate failed"),
                RuntimeError("render failed"),
            ])
    assert {type(exc) for exc in captured.value.exceptions} == {ValueError, RuntimeError}
    with cancellation.request_admission_lease():
        pass
