"""Characterize a shared K=1 admission gate across separate Python interpreters.

A multiprocessing Manager is a CI-only stand-in, not the proposed production
distributed lease coordinator. This test does not certify replica failure modes.
"""
import concurrent.futures
import multiprocessing
import os


def _hold_shared_permit(gate, acquired, finish):
    assert gate.acquire(False)
    acquired.set()
    assert finish.wait(10)
    gate.release()
    return os.getpid()


def _try_shared_permit(gate, acquired):
    assert acquired.wait(10)
    granted = gate.acquire(False)
    if granted:
        gate.release()
    return os.getpid(), granted


def test_shared_gate_denies_second_interpreter_and_recovers():
    context = multiprocessing.get_context("spawn")
    with context.Manager() as manager:
        gate = manager.BoundedSemaphore(1)
        acquired = manager.Event()
        finish = manager.Event()
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=2, mp_context=context
        ) as executor:
            holder = executor.submit(_hold_shared_permit, gate, acquired, finish)
            contender = executor.submit(_try_shared_permit, gate, acquired)
            try:
                contender_pid, granted = contender.result(timeout=20)
                assert not granted
            finally:
                finish.set()
            holder_pid = holder.result(timeout=20)
        assert holder_pid != contender_pid
        assert gate.acquire(False)
        gate.release()
