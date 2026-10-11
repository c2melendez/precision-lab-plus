"""Local prototype regressions; never count as DIST-01..08 certification."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from app.services.sg28_experimental_lease_coordinator import ExperimentalLeaseCoordinator


def test_atomic_single_slot_under_concurrent_threads():
    clock = lambda: 10.0
    coordinator = ExperimentalLeaseCoordinator(clock)
    barrier = Barrier(12)

    def attempt(i):
        barrier.wait(timeout=5)
        return coordinator.acquire(f"worker-{i}", 3)

    with ThreadPoolExecutor(max_workers=12) as pool:
        leases = list(pool.map(attempt, range(12)))
    valid = [lease for lease in leases if lease is not None]
    assert len(valid) == 1
    assert valid[0].generation == 1


def test_expiry_increases_generation_and_stale_release_cannot_revoke_successor():
    now = [50.0]
    coordinator = ExperimentalLeaseCoordinator(lambda: now[0])
    first = coordinator.acquire("a", 2)
    assert coordinator.acquire("b", 2) is None
    now[0] = 52.0
    second = coordinator.acquire("b", 2)
    assert second.generation == first.generation + 1
    assert coordinator.release(first) is False
    assert coordinator.acquire("c", 2) is None
    assert coordinator.release(second) is True
    third = coordinator.acquire("c", 2)
    assert third.generation == second.generation + 1


def test_owner_and_ttl_validation_before_state_mutation():
    coordinator = ExperimentalLeaseCoordinator(lambda: 20.0)
    import pytest
    for owner, ttl in [(None, 2), ("", 2), ("a", True), ("a", float("nan")),
                       ("a", float("inf")), ("a", 0), ("a", 11)]:
        with pytest.raises(ValueError):
            coordinator.acquire(owner, ttl)
    assert coordinator.acquire("valid", 2).generation == 1


def test_invalid_clock_fails_without_generating_lease():
    import pytest
    now = [float("nan")]
    coordinator = ExperimentalLeaseCoordinator(lambda: now[0])
    with pytest.raises(RuntimeError):
        coordinator.acquire("a", 2)
    now[0] = 7.0
    assert coordinator.acquire("a", 2).generation == 1


def test_release_reacquire_does_not_reuse_generation_for_same_owner():
    coordinator = ExperimentalLeaseCoordinator(lambda: 10.0)
    first = coordinator.acquire("same", 5)
    assert coordinator.release(first) is True
    second = coordinator.acquire("same", 5)
    assert second.generation > first.generation
    assert coordinator.release(first) is False
    assert coordinator.acquire("other", 5) is None


def test_expired_lease_cannot_release_new_owner_slot_at_boundary():
    now = [100.0]
    coordinator = ExperimentalLeaseCoordinator(lambda: now[0])
    old = coordinator.acquire("first", 1)
    now[0] = old.deadline
    new = coordinator.acquire("second", 1)
    assert new is not None and new.generation > old.generation
    assert coordinator.release(old) is False
    assert coordinator.acquire("third", 1) is None


def test_deadline_overflow_fails_closed_without_consuming_generation():
    import pytest
    now = [1.7976931348623157e308]
    coordinator = ExperimentalLeaseCoordinator(lambda: now[0])
    with pytest.raises(RuntimeError, match="overflow"):
        coordinator.acquire("a", 10)
    now[0] = 5.0
    lease = coordinator.acquire("b", 2)
    assert lease.generation == 1
    assert lease.deadline == 7.0
