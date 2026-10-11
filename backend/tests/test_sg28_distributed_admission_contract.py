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


def test_distributed_lease_covers_work_and_releases_after_completion(monkeypatch):
    monkeypatch.setenv("SG28_DISTRIBUTED_ADMISSION", "1")
    calls = []

    def exchange(payload):
        calls.append(dict(payload))
        return (
            {"granted": True, "generation": 11}
            if payload["op"] == "grant" else {"released": True}
        )

    with admission.distributed_admission_lease(exchange) as grant:
        assert grant.generation == 11
        assert calls == [{"op": "grant"}]
    assert calls == [
        {"op": "grant"}, {"op": "release", "generation": 11}
    ]


def test_distributed_lease_releases_on_worker_failure(monkeypatch):
    monkeypatch.setenv("SG28_DISTRIBUTED_ADMISSION", "1")
    calls = []

    def exchange(payload):
        calls.append(dict(payload))
        return {"granted": True, "generation": 3} if payload["op"] == "grant" else {"released": True}

    with pytest.raises(ValueError, match="worker failed"):
        with admission.distributed_admission_lease(exchange):
            raise ValueError("worker failed")
    assert calls[-1] == {"op": "release", "generation": 3}


@pytest.mark.parametrize("reply", [
    None, {}, {"released": False}, {"released": 1},
    {"released": True, "generation": 2}, {"granted": True, "generation": 2},
])
def test_distributed_release_requires_exact_ack(monkeypatch, reply):
    monkeypatch.setenv("SG28_DISTRIBUTED_ADMISSION", "1")
    with pytest.raises(admission.DistributedAdmissionUnavailable):
        admission.release_distributed_admission(
            lambda _: reply, admission.AdmissionGrant(generation=2)
        )


def test_distributed_release_error_never_confirms_success(monkeypatch):
    monkeypatch.setenv("SG28_DISTRIBUTED_ADMISSION", "1")

    def timeout(_):
        raise TimeoutError("ack lost")

    with pytest.raises(admission.DistributedAdmissionUnavailable):
        admission.release_distributed_admission(
            timeout, admission.AdmissionGrant(generation=2)
        )
