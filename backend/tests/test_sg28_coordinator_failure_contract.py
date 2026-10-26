"""SG28/H2 fail-closed coordination contract, CI-only model.

No production adapter is modified; injected outages model unavailable storage.
"""
import pytest


class CoordinationUnavailable(RuntimeError):
    pass


class AdmissionAdapter:
    def __init__(self, store):
        self.store = store

    def try_admit(self, owner):
        try:
            return bool(self.store.grant(owner))
        except (ConnectionError, TimeoutError, OSError) as exc:
            raise CoordinationUnavailable("shared coordinator unavailable") from exc


class FakeStore:
    def __init__(self, failure=None):
        self.failure = failure
        self.owner = None

    def grant(self, owner):
        if self.failure:
            raise self.failure
        if self.owner is not None:
            return False
        self.owner = owner
        return True


@pytest.mark.parametrize("failure", [
    ConnectionError("unreachable"),
    TimeoutError("coordination timeout"),
    OSError("connection reset"),
])
def test_coordinator_outage_fails_closed_instead_of_granting(failure):
    store = FakeStore(failure)
    with pytest.raises(CoordinationUnavailable):
        AdmissionAdapter(store).try_admit("worker-a")
    assert store.owner is None


def test_contender_denied_when_coordinator_tracks_active_owner():
    store = FakeStore()
    adapter = AdmissionAdapter(store)
    assert adapter.try_admit("worker-a")
    assert not adapter.try_admit("worker-b")
    assert store.owner == "worker-a"


def test_coordinator_recovers_without_granting_during_outage():
    """A transient fake coordinator outage must not silently admit requests."""
    store = FakeStore(ConnectionError("temporarily unavailable"))
    adapter = AdmissionAdapter(store)
    with pytest.raises(CoordinationUnavailable):
        adapter.try_admit("worker-a")
    assert store.owner is None

    store.failure = None
    assert adapter.try_admit("worker-b")
    assert not adapter.try_admit("worker-c")
    assert store.owner == "worker-b"


def test_coordinator_outage_does_not_erase_preexisting_owner():
    store = FakeStore()
    adapter = AdmissionAdapter(store)
    assert adapter.try_admit("worker-a")
    store.failure = TimeoutError("temporary outage")
    with pytest.raises(CoordinationUnavailable):
        adapter.try_admit("worker-b")
    assert store.owner == "worker-a"
    store.failure = None
    assert not adapter.try_admit("worker-b")
