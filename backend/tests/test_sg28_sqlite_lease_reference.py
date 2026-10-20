"""Disposable SQLite local reference tests; not multi-host DIST certification."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
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


def test_sqlite_release_fencing_survives_restart_after_expiry(tmp_path):
    path = tmp_path / "lease-restart.sqlite"
    now = [10.0]
    first_store = SqliteLeaseReference(path, lambda: now[0])
    old = first_store.acquire("same-owner", 2)
    now[0] = 12.0
    new_store = SqliteLeaseReference(path, lambda: now[0])
    new = new_store.acquire("same-owner", 2)
    assert new.generation == old.generation + 1
    assert first_store.release(old) is False
    assert SqliteLeaseReference(path, lambda: now[0]).acquire("racer", 2) is None
    assert new_store.release(new) is True


def test_sqlite_generation_persists_after_early_release_and_reopen(tmp_path):
    path = tmp_path / "lease-release.sqlite"
    first_store = SqliteLeaseReference(path, lambda: 10.0)
    first = first_store.acquire("owner", 5)
    assert first_store.release(first) is True
    reopened = SqliteLeaseReference(path, lambda: 10.0)
    second = reopened.acquire("owner", 5)
    assert second.generation == first.generation + 1
    assert reopened.release(first) is False


def test_sqlite_rejects_invalid_database_paths():
    import pytest
    for value in (None, "", 42, True):
        with pytest.raises(ValueError):
            SqliteLeaseReference(value, lambda: 1.0)


def test_sqlite_connections_closed_on_success_rejection_and_error(tmp_path, monkeypatch):
    import pytest
    import sqlite3
    from app.services.sg28_sqlite_lease_reference import SqliteLeaseReference

    class TrackedConnection(sqlite3.Connection):
        def close(self):
            closed.append(self)
            return super().close()

    closed = []
    store = SqliteLeaseReference(tmp_path / "tracked.sqlite", lambda: 10.0)
    def tracked_connect():
        return sqlite3.connect(store.db_path, timeout=2, isolation_level=None, factory=TrackedConnection)
    monkeypatch.setattr(store, "_connect", tracked_connect)
    lease = store.acquire("a", 2)
    assert store.acquire("b", 2) is None
    assert store.release(lease) is True
    assert store.release(lease) is False
    store.clock = lambda: float("nan")
    with pytest.raises(RuntimeError):
        store.acquire("c", 2)
    assert len(closed) == 5


def test_sqlite_release_rejects_boolean_generation_and_deadline_alias(tmp_path):
    import pytest
    from app.services.shared_admission_contract import SharedLease
    path = tmp_path / "type-alias.sqlite"
    store = SqliteLeaseReference(path, lambda: 0.0)
    lease = store.acquire("a", 1)
    assert lease.generation == 1 and lease.deadline == 1.0
    with pytest.raises(ValueError):
        store.release(SharedLease("a", True, lease.deadline))
    with pytest.raises(ValueError):
        store.release(SharedLease("a", lease.generation, True))
    assert store.acquire("b", 1) is None
    assert store.release(lease) is True


def test_sqlite_generation_exhaustion_fails_closed(tmp_path):
    import pytest
    import sqlite3
    path = tmp_path / "exhaustion.sqlite"
    store = SqliteLeaseReference(path, lambda: 10.0)
    with sqlite3.connect(path) as conn:
        conn.execute("UPDATE lease_state SET generation=? WHERE slot=1", (9223372036854775807,))
    with pytest.raises(RuntimeError, match="generation exhausted"):
        store.acquire("a", 2)
    with sqlite3.connect(path) as conn:
        assert conn.execute("SELECT owner,generation FROM lease_state WHERE slot=1").fetchone() == (None, 9223372036854775807)


def test_sqlite_lease_persists_across_independent_local_processes(tmp_path):
    """Local multi-process proof only: not an independent-host DIST gate."""
    import json
    import os
    import subprocess
    import sys

    path = tmp_path / "separate-processes.sqlite"
    # Child `python -c` processes do not inherit pytest's `pythonpath` ini
    # option (backend/pyproject.toml); pin the backend root explicitly so
    # `import app...` resolves regardless of the invocation cwd.
    backend_root = str(Path(__file__).resolve().parents[1])
    child_env = {**os.environ, "PYTHONPATH": backend_root}
    script = (
        "import json,sys\n"
        "from app.services.sg28_sqlite_lease_reference import SqliteLeaseReference\n"
        "store=SqliteLeaseReference(sys.argv[1],lambda:float(sys.argv[2]))\n"
        "lease=store.acquire(sys.argv[3],5)\n"
        "print(json.dumps(None if lease is None else [lease.owner,lease.generation,lease.deadline]))\n"
    )
    def acquire_in_process(owner, now):
        result = subprocess.run(
            [sys.executable, "-c", script, str(path), str(now), owner],
            check=True, capture_output=True, text=True, timeout=10, env=child_env,
        )
        return json.loads(result.stdout.strip())

    first = acquire_in_process("process-a", 10)
    assert first == ["process-a", 1, 15.0]
    assert acquire_in_process("process-b", 10) is None
    successor = acquire_in_process("process-b", 15)
    assert successor == ["process-b", 2, 20.0]
    assert acquire_in_process("process-c", 15) is None
