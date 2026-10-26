"""SG28 experimental shared-admission contract; NOT wired into public API.

An external coordinator implementation must provide atomic global leases.
This module intentionally defines only the client-side fail-closed boundary:
no loopback SQLite fixture is a substitute for multi-host infrastructure.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class SharedAdmissionUnavailable(RuntimeError):
    """Admission cannot be proven; caller MUST NOT start computation."""


class SharedAdmissionRejected(RuntimeError):
    """The verified shared capacity is already occupied."""


@dataclass(frozen=True)
class SharedLease:
    owner: str
    generation: int
    deadline: float


class SharedLeaseStore(Protocol):
    def acquire(self, owner: str, ttl: float) -> SharedLease | None: ...
    def release(self, lease: SharedLease) -> bool: ...


class SharedAdmissionClient:
    """A strict deny-by-default facade for a future networked lease store.

    It must be used ONLY after the store is independently validated and connected
    explicitly; the current evaluate endpoint continues to use local admission.
    """

    def __init__(self, store: SharedLeaseStore):
        self._store = store

    def acquire(self, owner: str, ttl: float) -> SharedLease:
        if not isinstance(owner, str) or not owner or type(ttl) not in (int, float) or not (0 < ttl <= 10):
            raise ValueError("owner and bounded positive ttl required")
        try:
            lease = self._store.acquire(owner, ttl)
        except Exception as exc:
            raise SharedAdmissionUnavailable("shared coordinator unavailable") from exc
        if lease is None:
            raise SharedAdmissionRejected("shared admission capacity exhausted")
        if (
            not isinstance(lease, SharedLease)
            or lease.owner != owner
            or type(lease.generation) is not int
            or lease.generation < 1
            or type(lease.deadline) not in (int, float)
            or not 0 < lease.deadline < float("inf")
        ):
            raise SharedAdmissionUnavailable("invalid shared lease response")
        return lease

    def release(self, lease: SharedLease) -> bool:
        if (
            not isinstance(lease, SharedLease)
            or not isinstance(lease.owner, str)
            or not lease.owner
            or type(lease.generation) is not int
            or lease.generation < 1
            or type(lease.deadline) not in (int, float)
            or not 0 < lease.deadline < float("inf")
        ):
            raise SharedAdmissionUnavailable("invalid shared lease release request")
        try:
            result = self._store.release(lease)
        except Exception as exc:
            raise SharedAdmissionUnavailable("shared coordinator release uncertain") from exc
        if type(result) is not bool:
            raise SharedAdmissionUnavailable("invalid shared release response")
        return result
