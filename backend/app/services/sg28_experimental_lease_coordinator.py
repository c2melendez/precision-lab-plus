"""Isolated SG28 lease-state prototype; not a distributed coordinator.

For disposable, single-process characterization ONLY. Does not provide
durability, cross-host consensus, authentication or public API integration.
"""
from __future__ import annotations

import math
import threading
import time

from app.services.shared_admission_contract import SharedLease


class ExperimentalLeaseCoordinator:
    """Single-slot atomic leases with monotonic expiration and fencing."""

    def __init__(self, clock=None):
        self._clock = clock or time.monotonic
        self._lock = threading.Lock()
        self._active: SharedLease | None = None
        self._generation = 0

    def acquire(self, owner: str, ttl: float) -> SharedLease | None:
        if not isinstance(owner, str) or not owner or type(ttl) not in (int, float) or not math.isfinite(ttl) or not 0 < ttl <= 10:
            raise ValueError("invalid lease request")
        with self._lock:
            now = self._clock()
            if not math.isfinite(now):
                raise RuntimeError("coordinator clock unavailable")
            if self._active is not None and now < self._active.deadline:
                return None
            deadline = now + ttl
            if not math.isfinite(deadline) or deadline <= now:
                raise RuntimeError("coordinator deadline not representable")
            self._generation += 1
            self._active = SharedLease(owner, self._generation, deadline)
            return self._active

    def release(self, lease: SharedLease) -> bool:
        with self._lock:
            if self._active is None or lease != self._active:
                return False
            self._active = None
            return True
