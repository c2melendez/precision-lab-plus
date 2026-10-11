"""Disposable single-host SQLite lease reference for SG28, NOT a network coordinator.

This exercises transactional persistence and fencing across local process restarts.
Uses a caller-supplied clock representing ONE coordinator's persistent time base.
No cross-host clock guarantees, authentication, HTTP integration, or production use.
"""
from __future__ import annotations

import math
import os
import sqlite3
from contextlib import closing

from app.services.shared_admission_contract import SharedLease


class SqliteLeaseReference:
    def __init__(self, db_path: str, clock):
        if not isinstance(db_path, (str, os.PathLike)) or not str(db_path):
            raise ValueError("persistent lease database path required")
        self.db_path = str(db_path)
        self.clock = clock
        with closing(self._connect()) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS lease_state ("
                "slot INTEGER PRIMARY KEY CHECK (slot=1), "
                "owner TEXT, generation INTEGER NOT NULL, deadline REAL NOT NULL)"
            )
            conn.execute(
                "INSERT OR IGNORE INTO lease_state(slot,owner,generation,deadline) "
                "VALUES (1,NULL,0,0)"
            )

    def _connect(self):
        conn = sqlite3.connect(self.db_path, timeout=2, isolation_level=None)
        conn.execute("PRAGMA busy_timeout=2000")
        return conn

    def acquire(self, owner: str, ttl: float) -> SharedLease | None:
        if not isinstance(owner, str) or not owner or type(ttl) not in (float, int) or not math.isfinite(ttl) or not 0 < ttl <= 10:
            raise ValueError("invalid lease request")
        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                now = self.clock()
                if type(now) not in (int, float) or not math.isfinite(now):
                    raise RuntimeError("invalid coordinator clock")
                row = conn.execute("SELECT owner,generation,deadline FROM lease_state WHERE slot=1").fetchone()
                if row[0] is not None and now < row[2]:
                    conn.execute("ROLLBACK")
                    return None
                deadline = now + ttl
                if not math.isfinite(deadline) or deadline <= now:
                    raise RuntimeError("invalid lease deadline")
                if type(row[1]) is not int or row[1] < 0 or row[1] >= 9223372036854775807:
                    raise RuntimeError("lease generation exhausted or corrupt")
                generation = row[1] + 1
                conn.execute(
                    "UPDATE lease_state SET owner=?,generation=?,deadline=? WHERE slot=1",
                    (owner, generation, deadline),
                )
                conn.execute("COMMIT")
                return SharedLease(owner, generation, deadline)
            except BaseException:
                if conn.in_transaction:
                    conn.execute("ROLLBACK")
                raise

    def release(self, lease: SharedLease) -> bool:
        if (not isinstance(lease, SharedLease) or not isinstance(lease.owner, str)
                or not lease.owner or type(lease.generation) is not int
                or lease.generation < 1 or type(lease.deadline) not in (int, float)
                or not math.isfinite(lease.deadline) or lease.deadline <= 0):
            raise ValueError("invalid lease")
        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                row = conn.execute("SELECT owner,generation,deadline FROM lease_state WHERE slot=1").fetchone()
                matched = (row[0], row[1], row[2]) == (lease.owner, lease.generation, lease.deadline)
                if matched:
                    conn.execute("UPDATE lease_state SET owner=NULL WHERE slot=1")
                conn.execute("COMMIT")
                return matched
            except BaseException:
                if conn.in_transaction:
                    conn.execute("ROLLBACK")
                raise
