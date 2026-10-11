"""Disposable SQLite local reference tests; not multi-host DIST certification."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from app.services.sg28_sqlite_lease_reference import SqliteLeaseReference


def test_lease_survives_coordinator_object_restart(tmp_path):
    path = tmp_path / "leases.sqlite"
    now = [100.0]
    first_store = SqliteLeaseReference(path, lambda: now[0])
    first = first_store.acquire("worker-a", 5)
    restarted = SqliteLeaseReference(path, lambda: now[0])
    assert restarted.acquire("worker-b", 5) is None
    now[0] = 105.0
    second = restarted.acquire("worker-b", 5)
    assert second.generation == first.generation + 1
    assert first_store.release(first) is False
    assert restarted.acquire("worker-c", 5) is None
    assert restarted.release(second) is True
    assert SqliteLeaseReference(path, lambda: now[0]).acquire("worker-c", 5).generation == 3


def test_sqlite_atomic_single_slot_across_distinct_connections(tmp_path):
    path = tmp_path / "leases.sqlite"
    clock = lambda: 10.0
    stores = [SqliteLeaseReference(path, clock) for _ in range(8)]
    barrier = Barrier(8)

    def request(i):
        barrier.wait(timeout=10)
        return stores[i].acquire(f"worker-{i}", 3)

    with ThreadPoolExecutor(max_workers=8) as pool:
        leases = list(pool.map(request, range(8)))
    granted = [lease for lease in leases if lease is not None]
    assert len(granted) == 1
    assert granted[0].generation == 1


def test_failed_clock_rolls_back_transaction_and_counter(tmp_path):
    import pytest
    path = tmp_path / "leases.sqlite"
    now = [float("nan")]
    store = SqliteLeaseReference(path, lambda: now[0])
    with pytest.raises(RuntimeError):
        store.acquire("bad", 1)
    now[0] = 1.0
    assert store.acquire("good", 1).generation == 1
