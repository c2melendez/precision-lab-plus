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


@pytest.mark.parametrize("host", ["localhost", "127.0.0.1", "::1"])
def test_disposable_remote_probe_never_accepts_local_host(tmp_path, host):
    with pytest.raises(DistributedAdmissionUnavailable, match="non-loopback"):
        assess(_config(tmp_path, host=host), explicitly_disposable=True)


@pytest.mark.parametrize("port", [0, -1, 65536])
def test_disposable_remote_probe_rejects_invalid_port(tmp_path, port):
    config = _config(tmp_path)
    invalid = CoordinatorTLSConfig(config.host, port, config.server_name,
                                   config.ca_file, config.client_cert_file,
                                   config.client_key_file)
    with pytest.raises(DistributedAdmissionUnavailable, match="address"):
        assess(invalid, explicitly_disposable=True)


def test_disposable_remote_probe_does_not_contact_coordinator(tmp_path, monkeypatch):
    import socket

    def unexpected_connection(*args, **kwargs):
        raise AssertionError("static readiness must not open network sockets")

    monkeypatch.setattr(socket, "create_connection", unexpected_connection)
    result = assess(_config(tmp_path), explicitly_disposable=True)
    assert result["network_test_executed"] is False
    assert result["dist01_certified"] is False


@pytest.mark.parametrize("server_name", ["", "localhost", "127.0.0.1", "::1"])
def test_remote_probe_requires_nonlocal_server_identity(tmp_path, server_name):
    config = _config(tmp_path)
    invalid = CoordinatorTLSConfig(config.host, config.port, server_name,
                                   config.ca_file, config.client_cert_file,
                                   config.client_key_file)
    with pytest.raises(DistributedAdmissionUnavailable):
        assess(invalid, explicitly_disposable=True)


@pytest.mark.parametrize("host", [
    "127.0.0.2", "0.0.0.0", "::", "::ffff:127.0.0.1",
    "169.254.1.7", "fe80::1", "localhost.", "sub.localhost",
])
def test_remote_probe_rejects_alternate_local_host_notation(tmp_path, host):
    with pytest.raises(DistributedAdmissionUnavailable, match="non-loopback"):
        assess(_config(tmp_path, host=host), explicitly_disposable=True)


@pytest.mark.parametrize("server_name", [
    "127.0.0.2", "0.0.0.0", "::", "::ffff:127.0.0.1",
    "fe80::1", "localhost.", "sub.localhost",
])
def test_remote_probe_rejects_alternate_local_tls_identity(tmp_path, server_name):
    config = _config(tmp_path)
    invalid = CoordinatorTLSConfig(config.host, config.port, server_name,
                                   config.ca_file, config.client_cert_file,
                                   config.client_key_file)
    with pytest.raises(DistributedAdmissionUnavailable, match="non-loopback"):
        assess(invalid, explicitly_disposable=True)

@pytest.mark.parametrize("host", ["224.0.0.1", "239.255.255.250", "ff02::1"])
def test_remote_probe_rejects_multicast_coordinator(tmp_path, host):
    with pytest.raises(DistributedAdmissionUnavailable, match="non-loopback"):
        assess(_config(tmp_path, host=host), explicitly_disposable=True)


@pytest.mark.parametrize("server_name", ["224.0.0.1", "ff02::1"])
def test_remote_probe_rejects_multicast_tls_identity(tmp_path, server_name):
    config = _config(tmp_path)
    invalid = CoordinatorTLSConfig(config.host, config.port, server_name,
                                   config.ca_file, config.client_cert_file,
                                   config.client_key_file)
    with pytest.raises(DistributedAdmissionUnavailable, match="non-loopback"):
        assess(invalid, explicitly_disposable=True)


@pytest.mark.parametrize("invalid", [None, 12, True, [], {}, " ", "\t"])
@pytest.mark.parametrize("field", ["host", "server_name"])
def test_remote_probe_invalid_identity_types_fail_closed(tmp_path, invalid, field):
    config = _config(tmp_path)
    values = {
        "host": config.host, "port": config.port,
        "server_name": config.server_name,
        "ca_file": config.ca_file,
        "client_cert_file": config.client_cert_file,
        "client_key_file": config.client_key_file,
    }
    values[field] = invalid
    with pytest.raises(DistributedAdmissionUnavailable, match="address"):
        assess(CoordinatorTLSConfig(**values), explicitly_disposable=True)


@pytest.mark.parametrize("host", ["127.1", "127.0.1", "2130706433", "0177.0.0.1", "0x7f000001"])
def test_remote_probe_rejects_legacy_ipv4_loopback_spellings(tmp_path, host):
    with pytest.raises(DistributedAdmissionUnavailable, match="non-loopback"):
        assess(_config(tmp_path, host=host), explicitly_disposable=True)


@pytest.mark.parametrize("server_name", ["127.1", "2130706433", "0x7f000001"])
def test_remote_probe_rejects_legacy_ipv4_tls_identity(tmp_path, server_name):
    config = _config(tmp_path)
    invalid = CoordinatorTLSConfig(config.host, config.port, server_name,
                                   config.ca_file, config.client_cert_file,
                                   config.client_key_file)
    with pytest.raises(DistributedAdmissionUnavailable, match="non-loopback"):
        assess(invalid, explicitly_disposable=True)
