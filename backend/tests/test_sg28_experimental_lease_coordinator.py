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
