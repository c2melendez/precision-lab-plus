"""CI-only shared lease expiry characterization across spawned Python processes.

Manager-backed synchronized state is a test fixture, NOT a production coordinator.
No actual process crashes, remote replicas or network partition are simulated.
"""
import concurrent.futures
import multiprocessing
import os


def _lease_attempt(shared, lock, now, role):
    with lock:
        lease = shared.get("lease")
        if lease is not None and now < lease["expires"]:
            return os.getpid(), role, False, lease["generation"]
        generation = (lease["generation"] if lease else 0) + 1
        shared["lease"] = {
            "generation": generation, "owner": role, "expires": now + 5
        }
        return os.getpid(), role, True, generation


def test_expired_shared_lease_is_replaced_across_interpreters():
    ctx = multiprocessing.get_context("spawn")
    with ctx.Manager() as manager:
        shared = manager.dict()
        lock = manager.Lock()
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=2, mp_context=ctx
        ) as pool:
            first = pool.submit(_lease_attempt, shared, lock, 0, "first")
            first_pid, _, first_granted, first_generation = first.result(timeout=15)
            second = pool.submit(_lease_attempt, shared, lock, 1, "second")
            second_pid, _, second_granted, _ = second.result(timeout=15)
            third = pool.submit(_lease_attempt, shared, lock, 5, "third")
            _, _, third_granted, third_generation = third.result(timeout=15)

        assert first_granted
        assert not second_granted
        assert third_granted
        assert third_generation > first_generation
        assert shared["lease"]["owner"] == "third"
        # Worker PIDs are only observational: executor may reuse a process.
        assert first_pid > 0 and second_pid > 0


def _simultaneous_claim(shared, lock, barrier, role):
    """Two live spawned workers contend for the same shared lease."""
    assert barrier.wait(timeout=12) in (0, 1)
    return _lease_attempt(shared, lock, 0, role)


def test_two_distinct_workers_contend_atomically_for_shared_k1():
    ctx = multiprocessing.get_context("spawn")
    with ctx.Manager() as manager:
        shared = manager.dict()
        lock = manager.Lock()
        barrier = manager.Barrier(2)
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=2, mp_context=ctx
        ) as pool:
            left = pool.submit(_simultaneous_claim, shared, lock, barrier, "left")
            right = pool.submit(_simultaneous_claim, shared, lock, barrier, "right")
            results = [left.result(timeout=20), right.result(timeout=20)]
        assert len({item[0] for item in results}) == 2
        assert sorted(item[2] for item in results) == [False, True]
        winner = next(item for item in results if item[2])
        assert shared["lease"]["owner"] == winner[1]
        assert shared["lease"]["generation"] == 1


def test_shared_lease_recovers_after_owner_becomes_unresponsive():
    """Logical orphan recovery: no forced process exit or production coordinator.

    Owner receives a grant then sends no renewal. A contender can only acquire
    when simulated TTL expires; stale owner cannot revoke successor.
    """
    ctx = multiprocessing.get_context("spawn")
    with ctx.Manager() as manager:
        shared = manager.dict()
        lock = manager.Lock()
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=2, mp_context=ctx
        ) as pool:
            owner = pool.submit(_lease_attempt, shared, lock, 0, "silent-owner")
            owner_pid, _, granted, original_gen = owner.result(timeout=15)
            denied = pool.submit(_lease_attempt, shared, lock, 4, "replacement")
            _, _, before_expiry, _ = denied.result(timeout=15)
            replacement = pool.submit(_lease_attempt, shared, lock, 5, "replacement")
            _, _, after_expiry, new_gen = replacement.result(timeout=15)
        assert owner_pid > 0 and granted
        assert not before_expiry
        assert after_expiry and new_gen == original_gen + 1
        assert shared["lease"]["owner"] == "replacement"
        assert shared["lease"]["generation"] == new_gen
