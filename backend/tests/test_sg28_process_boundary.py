"""SG28/H2 characterization: two distinct processes can hold local K=1 leases.

This proves that the current worker-local semaphores do NOT enforce a global
K=1 budget. Not a distributed admission or production-topology acceptance gate.
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
    os.environ["SG28_MAX_ISOLATED_REQUESTS"] = "1"
    os.environ["SG28_EVALUATE_ISOLATION"] = "0"
    from app.services.request_cancellation import (
        IsolationCapacityExceeded,
        request_admission_lease,
    )

    with request_admission_lease():
        try:
            with request_admission_lease():
                rejected = False
        except IsolationCapacityExceeded:
            rejected = True
        ready.append(os.getpid())
        deadline = time.monotonic() + 12
        while len(ready) < 2:
            if time.monotonic() > deadline:
                raise AssertionError("Second process did not acquire local lease")
            time.sleep(0.02)
    with request_admission_lease():
        recovered = True
    return worker_id, os.getpid(), rejected, recovered


def test_two_python_processes_hold_independent_local_k1_leases():
    with multiprocessing.Manager() as manager:
        ready = manager.list()
        with concurrent.futures.ProcessPoolExecutor(max_workers=2) as pool:
            tasks = [pool.submit(_hold_local_slot, ready, index) for index in (0, 1)]
            results = [task.result(timeout=25) for task in tasks]
    assert sorted(result[0] for result in results) == [0, 1]
    assert len({result[1] for result in results}) == 2
    assert all(rejected and recovered for _, _, rejected, recovered in results)
