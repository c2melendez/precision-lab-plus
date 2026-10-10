"""SG28/H2: cross-process characterization of worker-local admission.

This intentionally proves two independent interpreters each have their own K=1
pool. It is evidence of a missing global quota, not fleet-wide certification.
"""
import concurrent.futures
import os
from pathlib import Path
import sys

_BACKEND = str(Path(__file__).resolve().parents[1])


def _claim_local_slot(worker_id: int) -> tuple[int, bool, bool]:
    """Executed inside a separate interpreter via ProcessPoolExecutor."""
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
    with request_admission_lease():
        recovered = True
    return worker_id, rejected, recovered


def test_sg28_independent_python_processes_have_local_k1_capacity():
    with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(_claim_local_slot, idx) for idx in (0, 1)]
        results = [future.result(timeout=20) for future in futures]
    assert sorted(results) == [(0, True, True), (1, True, True)]
