"""SG28/H2: independently initialized Python processes hold concurrent local K=1 leases.

Characterizes the absence of a fleet-wide quota; NOT production certification.
The spawn context prevents inherited module-level admission state from fork.
"""
import concurrent.futures
import multiprocessing
import os
from pathlib import Path
import sys
import time

_BACKEND = str(Path(__file__).resolve().parents[1])


def _hold_local_slot(ready, worker_id):
    sys.path.insert(0, _BACKEND)
    from app.services import request_cancellation as admission

    assert admission._MAX_ISOLATED_REQUESTS == 1
    with admission.request_admission_lease():
        try:
            with admission.request_admission_lease():
                rejected = False
        except admission.IsolationCapacityExceeded:
            rejected = True
        ready.append(os.getpid())
        deadline = time.monotonic() + 12
        while len(ready) < 2:
            if time.monotonic() > deadline:
                raise AssertionError("Second process did not acquire its local lease")
            time.sleep(0.02)
    with admission.request_admission_lease():
        recovered = True
    return worker_id, os.getpid(), rejected, recovered


def test_two_python_processes_hold_independent_local_k1_leases(monkeypatch):
    monkeypatch.setenv("SG28_MAX_ISOLATED_REQUESTS", "1")
    monkeypatch.setenv("SG28_EVALUATE_ISOLATION", "0")
    context = multiprocessing.get_context("spawn")
    with context.Manager() as manager:
        ready = manager.list()
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=2, mp_context=context
        ) as pool:
            tasks = [pool.submit(_hold_local_slot, ready, index) for index in (0, 1)]
            results = [task.result(timeout=25) for task in tasks]
    assert sorted(result[0] for result in results) == [0, 1]
    assert len({result[1] for result in results}) == 2
    assert all(rejected and recovered for _, _, rejected, recovered in results)
