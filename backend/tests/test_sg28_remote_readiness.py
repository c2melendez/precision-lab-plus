"""SG28 cross-runner staging readiness is fail-closed and never a DIST PASS."""
import pytest

from app.services.distributed_admission import DistributedAdmissionUnavailable
from app.services.distributed_tls_transport import CoordinatorTLSConfig
from qa.sg28_remote_readiness import assess


def _config(tmp_path, host="staging.internal"):
    paths = [tmp_path / name for name in ("ca.pem", "client.pem", "key.pem")]
    for path in paths:
        path.write_text("placeholder for static validation", encoding="utf-8")
    return CoordinatorTLSConfig(host, 443, "coordinator.staging.internal",
                                *(str(path) for path in paths))


def test_remote_probe_requires_disposable_authorization(tmp_path):
    with pytest.raises(DistributedAdmissionUnavailable, match="authorization required"):
        assess(_config(tmp_path), explicitly_disposable=False)


def test_remote_probe_rejects_loopback_as_distributed_evidence(tmp_path):
    with pytest.raises(DistributedAdmissionUnavailable, match="non-loopback"):
        assess(_config(tmp_path, host="127.0.0.1"), explicitly_disposable=True)


def test_remote_probe_does_not_claim_network_or_dist_certification(tmp_path):
    result = assess(_config(tmp_path), explicitly_disposable=True)
    assert result["ready_for_connectivity_probe"] is True
    assert result["tls_identity_check_configured"] is True
    assert result["network_test_executed"] is False
    assert result["dist01_certified"] is False


def test_remote_probe_requires_all_trust_material(tmp_path):
    config = _config(tmp_path)
    (tmp_path / "key.pem").unlink()
    with pytest.raises(DistributedAdmissionUnavailable, match="trust material missing"):
        assess(config, explicitly_disposable=True)
