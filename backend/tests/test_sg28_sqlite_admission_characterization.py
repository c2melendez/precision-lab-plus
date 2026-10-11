"""SG28/H2: SQLite transaction-backed admission characterization (CI only).

SQLite is a disposable shared-storage fixture. It is not a production
multi-host coordinator and does not replace a distributed lease service.
"""
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor


def _connect(db):
    con = sqlite3.connect(db, timeout=5, isolation_level=None)
    con.execute("PRAGMA busy_timeout=5000")
    return con


def _grant(db, owner, now, ttl):
    con = _connect(db)
    try:
        con.execute("BEGIN IMMEDIATE")
        row = con.execute(
            "SELECT owner, generation, deadline FROM active_lease WHERE id=1"
        ).fetchone()
        if row and now < row[2]:
            con.execute("COMMIT")
            return None
        generation = (row[1] if row else 0) + 1
        con.execute(
            "INSERT INTO active_lease(id, owner, generation, deadline) "
            "VALUES(1, ?, ?, ?) ON CONFLICT(id) DO UPDATE SET "
            "owner=excluded.owner, generation=excluded.generation, "
            "deadline=excluded.deadline",
            (owner, generation, now + ttl),
        )
        con.execute("COMMIT")
        return generation
    finally:
        con.close()


def _release(db, owner, generation):
    con = _connect(db)
    try:
        con.execute("BEGIN IMMEDIATE")
        affected = con.execute(
            "UPDATE active_lease SET deadline=-1 WHERE id=1 AND owner=? AND generation=? AND deadline>=0",
            (owner, generation),
        ).rowcount
        con.execute("COMMIT")
        return bool(affected)
    finally:
        con.close()


def test_atomic_storage_gate_denies_racing_k1_claims(tmp_path):
    db = str(tmp_path / "sg28.sqlite")
    with _connect(db) as con:
        con.execute(
            "CREATE TABLE active_lease(id INTEGER PRIMARY KEY, "
            "owner TEXT NOT NULL, generation INTEGER NOT NULL, "
            "deadline REAL NOT NULL)"
        )
    barrier = threading.Barrier(2)

    def contender(owner):
        barrier.wait(timeout=5)
        return owner, _grant(db, owner, 0, 10)

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(contender, x) for x in ("a", "b")]
        results = [f.result(timeout=10) for f in futures]
    winners = [(owner, gen) for owner, gen in results if gen is not None]
    assert len(winners) == 1
    owner, generation = winners[0]
    assert generation == 1
    assert not _release(db, "other", generation)
    assert _release(db, owner, generation)
    assert _grant(db, "next", 1, 10) == 2


def test_storage_gate_expiry_fences_stale_release(tmp_path):
    db = str(tmp_path / "sg28.sqlite")
    with _connect(db) as con:
        con.execute(
            "CREATE TABLE active_lease(id INTEGER PRIMARY KEY, "
            "owner TEXT NOT NULL, generation INTEGER NOT NULL, "
            "deadline REAL NOT NULL)"
        )
    old = _grant(db, "a", 0, 5)
    new = _grant(db, "b", 5, 5)
    assert new == old + 1
    assert not _release(db, "a", old)
    assert _grant(db, "c", 6, 5) is None


def _spawned_storage_contender(db, barrier, owner):
    import os
    barrier.wait(timeout=15)
    return os.getpid(), owner, _grant(db, owner, 0, 10)


def test_atomic_storage_gate_across_distinct_spawned_processes(tmp_path):
    """Two distinct spawned interpreters share one SQLite file and K=1."""
    import multiprocessing
    from concurrent.futures import ProcessPoolExecutor

    db = str(tmp_path / "multiprocess-sg28.sqlite")
    with _connect(db) as con:
        con.execute(
            "CREATE TABLE active_lease(id INTEGER PRIMARY KEY, "
            "owner TEXT NOT NULL, generation INTEGER NOT NULL, "
            "deadline REAL NOT NULL)"
        )
    ctx = multiprocessing.get_context("spawn")
    with ctx.Manager() as manager:
        barrier = manager.Barrier(2)
        with ProcessPoolExecutor(max_workers=2, mp_context=ctx) as pool:
            futures = [
                pool.submit(_spawned_storage_contender, db, barrier, owner)
                for owner in ("process-a", "process-b")
            ]
            results = [future.result(timeout=25) for future in futures]
    assert len({pid for pid, _, _ in results}) == 2
    winners = [(owner, generation) for _, owner, generation in results if generation is not None]
    assert len(winners) == 1
    assert winners[0][1] == 1
    with _connect(db) as con:
        assert con.execute("SELECT owner FROM active_lease WHERE id=1").fetchone()[0] == winners[0][0]


def test_storage_gate_concurrent_expiry_has_single_successor(tmp_path):
    """Expired lease has exactly one next-generation owner under contention."""
    db = str(tmp_path / "expired-sg28.sqlite")
    with _connect(db) as con:
        con.execute(
            "CREATE TABLE active_lease(id INTEGER PRIMARY KEY, "
            "owner TEXT NOT NULL, generation INTEGER NOT NULL, "
            "deadline REAL NOT NULL)"
        )
    assert _grant(db, "old-owner", 0, 5) == 1
    barrier = threading.Barrier(2)

    def contender(owner):
        barrier.wait(timeout=5)
        return owner, _grant(db, owner, 5, 5)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = [
            f.result(timeout=10)
            for f in (
                pool.submit(contender, "successor-a"),
                pool.submit(contender, "successor-b"),
            )
        ]
    winners = [(owner, generation) for owner, generation in results if generation is not None]
    assert len(winners) == 1
    assert winners[0][1] == 2
    assert not _release(db, "old-owner", 1)
    with _connect(db) as con:
        stored = con.execute(
            "SELECT owner, generation FROM active_lease WHERE id=1"
        ).fetchone()
    assert stored == winners[0]


def test_stale_owner_release_cannot_revoke_live_successor(tmp_path):
    """Old lease holder's delayed release cannot invalidate a live successor."""
    db = str(tmp_path / "fenced-release.sqlite")
    with _connect(db) as con:
        con.execute(
            "CREATE TABLE active_lease(id INTEGER PRIMARY KEY, "
            "owner TEXT NOT NULL, generation INTEGER NOT NULL, "
            "deadline REAL NOT NULL)"
        )
    first = _grant(db, "old", 0, 5)
    second = _grant(db, "new", 5, 10)
    assert (first, second) == (1, 2)
    assert not _release(db, "old", first)
    with _connect(db) as con:
        assert con.execute(
            "SELECT owner, generation, deadline FROM active_lease WHERE id=1"
        ).fetchone() == ("new", 2, 15)
    assert _grant(db, "third", 6, 10) is None
    assert _release(db, "new", second)
    assert _grant(db, "third", 6, 10) == 3


def test_same_owner_stale_generation_cannot_release_reacquired_lease(tmp_path):
    """Owner identity alone must not authorize releasing a later generation."""
    db = str(tmp_path / "same-owner-fencing.sqlite")
    with _connect(db) as con:
        con.execute(
            "CREATE TABLE active_lease(id INTEGER PRIMARY KEY, "
            "owner TEXT NOT NULL, generation INTEGER NOT NULL, "
            "deadline REAL NOT NULL)"
        )
    old_generation = _grant(db, "worker-a", 0, 5)
    current_generation = _grant(db, "worker-a", 5, 10)
    assert (old_generation, current_generation) == (1, 2)
    assert not _release(db, "worker-a", old_generation)
    with _connect(db) as con:
        assert con.execute(
            "SELECT owner, generation, deadline FROM active_lease WHERE id=1"
        ).fetchone() == ("worker-a", 2, 15)
    assert _grant(db, "worker-b", 6, 10) is None
    assert _release(db, "worker-a", current_generation)
    assert _grant(db, "worker-b", 6, 10) == 3


def _abrupt_storage_owner_exit(db, marker):
    """Acquire test-only lease and terminate without releasing it."""
    import os
    generation = _grant(db, "crashed-worker", 0, 5)
    if generation != 1:
        os._exit(21)
    with open(marker, "w", encoding="utf-8") as handle:
        handle.write(str(generation))
    os._exit(17)


def test_storage_lease_expires_after_abrupt_owner_process_exit(tmp_path):
    """Owner process death must not grant a successor before lease expiry."""
    import multiprocessing

    db = str(tmp_path / "abrupt-exit-sg28.sqlite")
    marker = str(tmp_path / "owner-granted.txt")
    with _connect(db) as con:
        con.execute(
            "CREATE TABLE active_lease(id INTEGER PRIMARY KEY, "
            "owner TEXT NOT NULL, generation INTEGER NOT NULL, "
            "deadline REAL NOT NULL)"
        )
    ctx = multiprocessing.get_context("spawn")
    owner = ctx.Process(target=_abrupt_storage_owner_exit, args=(db, marker))
    owner.start()
    owner.join(timeout=15)
    if owner.is_alive():
        owner.terminate()
        owner.join(timeout=5)
    assert owner.exitcode == 17
    assert (tmp_path / "owner-granted.txt").read_text(encoding="utf-8") == "1"
    assert _grant(db, "successor", 4, 5) is None
    assert _grant(db, "successor", 5, 5) == 2
    assert not _release(db, "crashed-worker", 1)
    with _connect(db) as con:
        assert con.execute(
            "SELECT owner, generation, deadline FROM active_lease WHERE id=1"
        ).fetchone() == ("successor", 2, 10)
