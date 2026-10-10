"""SG28/H2 test-only lease model: expiry, fencing and safe retries.

This is a deterministic contract characterization, not a production coordinator.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Lease:
    token: str
    generation: int
    deadline: float


class LeaseGate:
    def __init__(self):
        self.active = None
        self.generation = 0

    def acquire(self, token, now, ttl):
        assert ttl > 0
        if self.active and now < self.active.deadline:
            return None
        self.generation += 1
        self.active = Lease(token, self.generation, now + ttl)
        return self.active

    def renew(self, lease, now, ttl):
        if self.active != lease or now >= lease.deadline:
            return None
        self.active = Lease(lease.token, lease.generation, now + ttl)
        return self.active

    def release(self, lease):
        if self.active != lease:
            return False
        self.active = None
        return True


def test_expired_lease_can_be_replaced_and_stale_release_cannot_clear_successor():
    gate = LeaseGate()
    original = gate.acquire("worker-a", now=0, ttl=5)
    assert gate.acquire("worker-b", now=1, ttl=5) is None
    replacement = gate.acquire("worker-b", now=5, ttl=5)
    assert replacement.generation > original.generation
    assert not gate.release(original)
    assert gate.active == replacement
    assert gate.release(replacement)
    assert gate.acquire("worker-c", now=6, ttl=5)


def test_renewal_and_duplicate_release_are_fenced():
    gate = LeaseGate()
    first = gate.acquire("worker-a", now=0, ttl=5)
    renewed = gate.renew(first, now=4, ttl=5)
    assert renewed.deadline == 9
    assert not gate.release(first)
    assert gate.acquire("worker-b", now=6, ttl=5) is None
    assert gate.release(renewed)
    assert not gate.release(renewed)


def test_expired_lease_cannot_be_renewed_by_previous_owner():
    gate = LeaseGate()
    lease = gate.acquire("worker-a", now=0, ttl=2)
    assert gate.renew(lease, now=2, ttl=2) is None
    successor = gate.acquire("worker-b", now=2, ttl=2)
    assert successor.generation > lease.generation
    assert gate.renew(lease, now=2.5, ttl=2) is None
    assert gate.active == successor


def test_active_lease_rejects_reused_token_until_expiry():
    gate = LeaseGate()
    first = gate.acquire("same-owner", now=0, ttl=5)
    assert gate.acquire("same-owner", now=1, ttl=5) is None
    second = gate.acquire("same-owner", now=5, ttl=5)
    assert second.generation != first.generation
    assert not gate.release(first)
    assert gate.active == second


def test_expired_renewal_does_not_reopen_capacity_for_stale_owner():
    gate = LeaseGate()
    old = gate.acquire("worker-a", now=0, ttl=3)
    successor = gate.acquire("worker-b", now=3, ttl=8)
    assert successor is not None
    assert gate.renew(old, now=4, ttl=10) is None
    assert gate.acquire("worker-c", now=4, ttl=5) is None
    assert gate.active == successor


def test_nonpositive_ttl_is_rejected_without_mutating_active_lease():
    gate = LeaseGate()
    active = gate.acquire("worker-a", now=0, ttl=5)
    for invalid_ttl in (0, -1):
        try:
            gate.acquire("worker-b", now=1, ttl=invalid_ttl)
        except AssertionError:
            pass
        else:
            raise AssertionError("invalid lease duration unexpectedly accepted")
        assert gate.active == active
