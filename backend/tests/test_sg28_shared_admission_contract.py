"""CI-only tests for a future SG28 shared-admission client boundary.

NOT proof of a networked coordinator or multiple hosts.
"""
import pytest

from app.services.shared_admission_contract import (
    SharedAdmissionClient,
    SharedAdmissionRejected,
    SharedAdmissionUnavailable,
    SharedLease,
)


class Store:
    def __init__(self):
        self.active = None
        self.generation = 0
        self.outage = False

    def acquire(self, owner, ttl):
        if self.outage:
            raise ConnectionError("network outage")
        if self.active is not None:
            return None
        self.generation += 1
        self.active = SharedLease(owner, self.generation, ttl)
        return self.active

    def release(self, lease):
        if self.outage:
            raise TimeoutError("release acknowledgement lost")
        if lease != self.active:
            return False
        self.active = None
        return True


def test_shared_boundary_rejects_contention_and_recovers_after_release():
    store = Store()
    client = SharedAdmissionClient(store)
    first = client.acquire("a", 5)
    with pytest.raises(SharedAdmissionRejected):
        client.acquire("b", 5)
    assert client.release(first) is True
    assert client.acquire("b", 5).generation == 2
    assert client.release(first) is False
    assert store.active.owner == "b"


def test_shared_boundary_fails_closed_during_outage_with_existing_lease():
    store = Store()
    client = SharedAdmissionClient(store)
    first = client.acquire("a", 5)
    store.outage = True
    with pytest.raises(SharedAdmissionUnavailable):
        client.acquire("b", 5)
    with pytest.raises(SharedAdmissionUnavailable):
        client.release(first)
    assert store.active == first
    store.outage = False
    assert client.release(first) is True


@pytest.mark.parametrize("reply", [
    {"owner": "a", "generation": 1, "deadline": 5},
    SharedLease("wrong-owner", 1, 5),
    SharedLease("a", 0, 5),
    SharedLease("a", True, 5),
    SharedLease("a", 1.5, 5),
    SharedLease("a", 1, float("nan")),
    SharedLease("a", 1, float("inf")),
    SharedLease("a", 1, float("-inf")),
    SharedLease("a", 1, 0),
    SharedLease("a", 1, -1),
])
def test_shared_boundary_rejects_invalid_lease_as_unavailable(reply):
    class BadStore:
        def acquire(self, owner, ttl):
            return reply

    with pytest.raises(SharedAdmissionUnavailable):
        SharedAdmissionClient(BadStore()).acquire("a", 5)


@pytest.mark.parametrize("ttl", [0, -1, 11, True, False, "5", None, float("nan"), float("inf"), float("-inf")])
def test_shared_boundary_rejects_invalid_ttl_before_store_call(ttl):
    class MustNotCall:
        def acquire(self, owner, ttl):
            pytest.fail("must reject before contacting coordinator")

    with pytest.raises(ValueError):
        SharedAdmissionClient(MustNotCall()).acquire("a", ttl)


def test_shared_boundary_does_not_accept_non_boolean_release_ack():
    class BadStore:
        def release(self, lease):
            return 1

    with pytest.raises(SharedAdmissionUnavailable):
        SharedAdmissionClient(BadStore()).release(SharedLease("a", 1, 5))


@pytest.mark.parametrize("owner", ["", None, 12, True])
def test_shared_boundary_rejects_invalid_owner_before_store_call(owner):
    class MustNotCall:
        def acquire(self, owner, ttl):
            pytest.fail("must reject before contacting coordinator")

    with pytest.raises(ValueError):
        SharedAdmissionClient(MustNotCall()).acquire(owner, 5)


@pytest.mark.parametrize("lease", [
    None,
    {"owner": "a", "generation": 1, "deadline": 5},
    SharedLease("", 1, 5),
    SharedLease("a", 0, 5),
    SharedLease("a", True, 5),
    SharedLease("a", 1.5, 5),
    SharedLease("a", 1, True),
    SharedLease("a", 1, float("nan")),
    SharedLease("a", 1, float("inf")),
    SharedLease("a", 1, float("-inf")),
    SharedLease("a", 1, 0),
    SharedLease("a", 1, -1),
])
def test_shared_boundary_invalid_release_lease_never_contacts_store(lease):
    class MustNotCall:
        def release(self, lease):
            pytest.fail("invalid lease must not contact coordinator")

    with pytest.raises(SharedAdmissionUnavailable):
        SharedAdmissionClient(MustNotCall()).release(lease)
