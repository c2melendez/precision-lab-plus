"""Characterization of the non-wired distributed admission boundary."""
import pytest

from app.services import distributed_admission as admission


def test_distributed_admission_disabled_by_default(monkeypatch):
    monkeypatch.delenv("SG28_DISTRIBUTED_ADMISSION", raising=False)
    invoked = []
    with pytest.raises(admission.DistributedAdmissionUnavailable):
        admission.acquire_distributed_admission(
            lambda payload: invoked.append(payload) or {"granted": True, "generation": 1}
        )
    assert invoked == []


def test_distributed_admission_rejects_missing_transport(monkeypatch):
    monkeypatch.setenv("SG28_DISTRIBUTED_ADMISSION", "1")
    with pytest.raises(admission.DistributedAdmissionUnavailable):
        admission.acquire_distributed_admission(None)


@pytest.mark.parametrize("reply", [
    None, True, [], {"granted": False, "generation": None},
    {"granted": True}, {"granted": True, "generation": 0},
    {"granted": True, "generation": True},
    {"granted": True, "generation": "1"},
    {"granted": True, "generation": 1, "owner": "forged"},
])
def test_distributed_admission_rejects_ambiguous_grants(monkeypatch, reply):
    monkeypatch.setenv("SG28_DISTRIBUTED_ADMISSION", "1")
    with pytest.raises(admission.DistributedAdmissionUnavailable):
        admission.acquire_distributed_admission(lambda _: reply)


def test_distributed_admission_rejects_network_error(monkeypatch):
    monkeypatch.setenv("SG28_DISTRIBUTED_ADMISSION", "1")

    def fail(_):
        raise TimeoutError("coordinator outage")

    with pytest.raises(admission.DistributedAdmissionUnavailable):
        admission.acquire_distributed_admission(fail)


def test_distributed_admission_accepts_valid_generation_without_client_identity(monkeypatch):
    monkeypatch.setenv("SG28_DISTRIBUTED_ADMISSION", "1")
    seen = []
    grant = admission.acquire_distributed_admission(
        lambda payload: seen.append(payload) or {"granted": True, "generation": 7}
    )
    assert grant.generation == 7
    assert seen == [{"op": "grant"}]
