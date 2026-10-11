"""SQLite lease store characterization: disposable shared-host test only."""
from concurrent.futures import ThreadPoolExecutor
import threading

from app.services.sg28_sqlite_lease_store import SQLiteLeaseStore


def test_store_enforces_k1_and_fences_release(tmp_path):
    store = SQLiteLeaseStore(str(tmp_path / "leases.sqlite"), ttl=5)
    first = store.acquire("a", now=100)
    assert first.owner == "a" and first.generation == 1 and first.deadline == 105
    assert store.acquire("b", now=104) is None
    assert not store.release("b", 1)
    second = store.acquire("b", now=105)
    assert second.generation == 2
    assert not store.release("a", 1)
    assert store.acquire("c", now=106) is None
    assert store.release("b", 2)
    third = store.acquire("c", now=106)
    assert third.generation == 3


def test_store_concurrent_clients_share_one_slot(tmp_path):
    path = str(tmp_path / "race.sqlite")
    SQLiteLeaseStore(path, ttl=5)
    barrier = threading.Barrier(8)

    def contend(i):
        store = SQLiteLeaseStore(path, ttl=5)
        barrier.wait(timeout=10)
        return store.acquire(f"client-{i}", now=100)

    with ThreadPoolExecutor(max_workers=8) as pool:
        leases = list(pool.map(contend, range(8)))
    winners = [lease for lease in leases if lease is not None]
    assert len(winners) == 1
    assert winners[0].generation == 1
    assert SQLiteLeaseStore(path, ttl=5).acquire("late", now=101) is None


def test_store_restart_retains_active_lease(tmp_path):
    path = str(tmp_path / "restart.sqlite")
    original = SQLiteLeaseStore(path, ttl=10)
    assert original.acquire("a", now=50).generation == 1
    restored = SQLiteLeaseStore(path, ttl=10)
    assert restored.acquire("b", now=59) is None
    assert restored.acquire("b", now=60).generation == 2
    assert not original.release("a", 1)


def test_store_rejects_nonfinite_server_clock_without_mutating_lease(tmp_path):
    """Nonfinite/overflow times must not bypass a previously held global slot."""
    import math
    import pytest

    store = SQLiteLeaseStore(str(tmp_path / "nonfinite.sqlite"), ttl=10)
    first = store.acquire("first", now=100)
    assert first.generation == 1
    for bad_now in (math.nan, math.inf, -math.inf, True):
        with pytest.raises(ValueError, match="Invalid trusted lease parameters"):
            store.acquire("other", now=bad_now)
    assert store.acquire("other", now=105) is None
    assert store.release("first", 1)
    assert store.acquire("next", now=105).generation == 2
