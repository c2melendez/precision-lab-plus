"""SG28 disposable shared lease store for certification only.

Not connected to the public evaluate endpoint, and NOT a cross-host service.
SQLite transactions serialize grants within a shared filesystem/CI host.
"""
from __future__ import annotations

import math
import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class LeaseRecord:
    owner: str
    generation: int
    deadline: float


class SQLiteLeaseStore:
    def __init__(self, path: str, *, ttl: float = 10.0):
        if type(ttl) not in (int, float) or not math.isfinite(ttl) or not (0 < ttl <= 60):
            raise ValueError("TTL outside test policy")
        self.path = path
        self.ttl = ttl
        with self._connect() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS sg28_leases "
                "(id INTEGER PRIMARY KEY CHECK (id=1), owner TEXT NOT NULL, "
                "generation INTEGER NOT NULL, deadline REAL NOT NULL)"
            )

    def _connect(self):
        con = sqlite3.connect(self.path, timeout=5, isolation_level=None)
        con.execute("PRAGMA busy_timeout=5000")
        return con

    def acquire(self, owner: str, *, now: float) -> LeaseRecord | None:
        """Now must come from the trusted coordinator clock, not a remote client."""
        if (type(owner) is not str or not owner or type(now) not in (int, float)
                or not math.isfinite(now) or not math.isfinite(now + self.ttl)
                or now + self.ttl <= now):
            raise ValueError("Invalid trusted lease parameters")
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute(
                "SELECT generation, deadline FROM sg28_leases WHERE id=1"
            ).fetchone()
            if row is not None and now < row[1]:
                con.execute("COMMIT")
                return None
            generation = (row[0] if row else 0) + 1
            deadline = now + self.ttl
            con.execute(
                "INSERT INTO sg28_leases(id,owner,generation,deadline) "
                "VALUES(1,?,?,?) ON CONFLICT(id) DO UPDATE SET "
                "owner=excluded.owner,generation=excluded.generation,"
                "deadline=excluded.deadline",
                (owner, generation, deadline),
            )
            con.execute("COMMIT")
            return LeaseRecord(owner, generation, deadline)

    def release(self, owner: str, generation: int) -> bool:
        if type(owner) is not str or not owner or type(generation) is not int or generation < 1:
            return False
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            changed = con.execute(
                "UPDATE sg28_leases SET deadline=-1 WHERE id=1 AND owner=? "
                "AND generation=? AND deadline>=0",
                (owner, generation),
            ).rowcount
            con.execute("COMMIT")
            return changed == 1
