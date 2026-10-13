"""No-network regressions for explicit SG28 remote mTLS probe."""
import pytest
import ssl
from app.services.distributed_admission import DistributedAdmissionUnavailable
from app.services.distributed_tls_transport import CoordinatorTLSConfig
from qa.sg28_remote_handshake import probe

def _config(tmp_path):
    paths = [tmp_path / name for name in ("ca.pem", "client.pem", "key.pem")]
    for path in paths:
        path.write_text("static fixture only", encoding="utf-8")
    return CoordinatorTLSConfig("coordinator.staging.internal", 443,
                                "coordinator.staging.internal", *(str(p) for p in paths))

def test_denied_authorization_never_initializes_tls(tmp_path, monkeypatch):
    import ssl
    monkeypatch.setattr(ssl, "create_default_context", lambda *a, **k: pytest.fail("TLS initialized"))
    with pytest.raises(DistributedAdmissionUnavailable, match="authorization required"):
        probe(_config(tmp_path), explicitly_disposable=False)

def test_bad_local_host_never_initializes_tls(tmp_path, monkeypatch):
    import ssl
    monkeypatch.setattr(ssl, "create_default_context", lambda *a, **k: pytest.fail("TLS initialized"))
    c = _config(tmp_path)
    invalid = CoordinatorTLSConfig("127.0.0.1", c.port, c.server_name,
                                   c.ca_file, c.client_cert_file, c.client_key_file)
    with pytest.raises(DistributedAdmissionUnavailable, match="non-loopback"):
        probe(invalid, explicitly_disposable=True)

def test_tls_handshake_sends_no_admission_messages(tmp_path, monkeypatch):
    import socket
    import ssl
    class FakeSecure:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def settimeout(self, timeout): assert timeout == 2.0
        def getpeercert(self): return {"subject": ((("commonName", "coordinator.staging.internal"),),)}
        def send(self, *args): pytest.fail("protocol data transmitted")
        def sendall(self, *args): pytest.fail("protocol data transmitted")
        def recv(self, *args): pytest.fail("protocol data received")
    class FakePlain:
        def __enter__(self): return self
        def __exit__(self, *args): return False
    class FakeContext:
        def load_cert_chain(self, certfile, keyfile): pass
        def wrap_socket(self, plain, *, server_hostname):
            assert server_hostname == "coordinator.staging.internal"
            return FakeSecure()
    context = FakeContext()
    monkeypatch.setattr(ssl, "create_default_context", lambda *a, **k: context)
    monkeypatch.setattr(socket, "create_connection", lambda *a, **k: FakePlain())
    result = probe(_config(tmp_path), explicitly_disposable=True)
    assert result == {"mtls_handshake_verified": True, "admission_request_sent": False,
                      "dist01_certified": False, "dist08_certified": False}

def test_failed_tcp_does_not_claim_handshake(tmp_path, monkeypatch):
    import socket
    import ssl
    class FakeContext:
        def load_cert_chain(self, *args): pass
    monkeypatch.setattr(ssl, "create_default_context", lambda *a, **k: FakeContext())
    monkeypatch.setattr(socket, "create_connection", lambda *a, **k: (_ for _ in ()).throw(ConnectionRefusedError()))
    with pytest.raises(DistributedAdmissionUnavailable, match="handshake failed"):
        probe(_config(tmp_path), explicitly_disposable=True)


@pytest.mark.parametrize("peer_certificate", [None, {}])
def test_missing_peer_identity_fails_closed_without_admission(tmp_path, monkeypatch, peer_certificate):
    import socket
    import ssl
    class FakeSecure:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def settimeout(self, timeout): pass
        def getpeercert(self): return peer_certificate
        def sendall(self, *args): pytest.fail("admission message sent")
    class FakePlain:
        def __enter__(self): return self
        def __exit__(self, *args): return False
    class FakeContext:
        def load_cert_chain(self, *args): pass
        def wrap_socket(self, *args, **kwargs): return FakeSecure()
    monkeypatch.setattr(ssl, "create_default_context", lambda *a, **k: FakeContext())
    monkeypatch.setattr(socket, "create_connection", lambda *a, **k: FakePlain())
    with pytest.raises(DistributedAdmissionUnavailable, match="peer identity"):
        probe(_config(tmp_path), explicitly_disposable=True)


@pytest.mark.parametrize("failure", [TimeoutError("timeout"), ConnectionResetError("reset"),
                                      ssl.SSLError("handshake"), OSError("unreachable")])
def test_remote_handshake_transport_errors_fail_closed(tmp_path, monkeypatch, failure):
    import socket
    import ssl
    class FakeContext:
        def load_cert_chain(self, *args): pass
    monkeypatch.setattr(ssl, "create_default_context", lambda *a, **k: FakeContext())
    def raise_connection(*args, **kwargs):
        raise failure
    monkeypatch.setattr(socket, "create_connection", raise_connection)
    with pytest.raises(DistributedAdmissionUnavailable, match="handshake failed"):
        probe(_config(tmp_path), explicitly_disposable=True)


def test_tls_certificate_loading_failure_fails_closed_before_network(tmp_path, monkeypatch):
    import socket
    import ssl
    class FakeContext:
        def load_cert_chain(self, *args):
            raise ssl.SSLError("invalid client certificate")
    monkeypatch.setattr(ssl, "create_default_context", lambda *a, **k: FakeContext())
    monkeypatch.setattr(socket, "create_connection", lambda *a, **k: pytest.fail("network contacted"))
    with pytest.raises(DistributedAdmissionUnavailable, match="handshake failed"):
        probe(_config(tmp_path), explicitly_disposable=True)


def test_tls_context_creation_failure_fails_closed_before_network(tmp_path, monkeypatch):
    import socket
    import ssl
    def broken_context(*args, **kwargs):
        raise ssl.SSLError("invalid CA bundle")
    monkeypatch.setattr(ssl, "create_default_context", broken_context)
    monkeypatch.setattr(socket, "create_connection", lambda *a, **k: pytest.fail("network contacted"))
    with pytest.raises(DistributedAdmissionUnavailable, match="handshake failed"):
        probe(_config(tmp_path), explicitly_disposable=True)


def test_tls_server_hostname_is_checked_before_handshake_payload(tmp_path, monkeypatch):
    import socket
    import ssl
    class FakePlain:
        def __enter__(self): return self
        def __exit__(self, *args): return False
    class FakeContext:
        def load_cert_chain(self, *args): pass
        def wrap_socket(self, plain, *, server_hostname):
            assert server_hostname == "coordinator.staging.internal"
            raise ssl.SSLCertVerificationError("hostname mismatch")
    monkeypatch.setattr(ssl, "create_default_context", lambda *a, **k: FakeContext())
    monkeypatch.setattr(socket, "create_connection", lambda *a, **k: FakePlain())
    with pytest.raises(DistributedAdmissionUnavailable, match="handshake failed"):
        probe(_config(tmp_path), explicitly_disposable=True)


def test_ssl_context_forces_server_identity_verification(tmp_path, monkeypatch):
    import socket
    import ssl
    class FakePlain:
        def __enter__(self): return self
        def __exit__(self, *args): return False
    class FakeSecure:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def settimeout(self, timeout): pass
        def getpeercert(self): return {"subject": ((("commonName", "coordinator.staging.internal"),),)}
    class StrictContext:
        def __init__(self):
            self.verify_mode = ssl.CERT_NONE
            self.check_hostname = False
        def load_cert_chain(self, *args): pass
        def wrap_socket(self, plain, *, server_hostname):
            assert self.verify_mode == ssl.CERT_REQUIRED
            assert self.check_hostname is True
            assert server_hostname == "coordinator.staging.internal"
            return FakeSecure()
    context = StrictContext()
    monkeypatch.setattr(ssl, "create_default_context", lambda *a, **k: context)
    monkeypatch.setattr(socket, "create_connection", lambda *a, **k: FakePlain())
    result = probe(_config(tmp_path), explicitly_disposable=True)
    assert result["mtls_handshake_verified"] is True
    assert result["admission_request_sent"] is False


def test_tls_uses_configured_ca_and_bounded_tcp_timeout(tmp_path, monkeypatch):
    import socket
    observed = {}
    config = _config(tmp_path)
    class FakePlain:
        def __enter__(self): return self
        def __exit__(self, *args): return False
    class FakeSecure:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def settimeout(self, timeout):
            assert timeout == config.timeout_seconds
        def getpeercert(self):
            return {"subject": ((('commonName', config.server_name),),)}
    class FakeContext:
        verify_mode = ssl.CERT_NONE
        check_hostname = False
        def load_cert_chain(self, certfile, keyfile):
            assert (certfile, keyfile) == (config.client_cert_file, config.client_key_file)
        def wrap_socket(self, plain, *, server_hostname):
            assert server_hostname == config.server_name
            assert self.verify_mode == ssl.CERT_REQUIRED
            assert self.check_hostname is True
            return FakeSecure()
    def context_factory(purpose, *, cafile):
        observed["context"] = (purpose, cafile)
        return FakeContext()
    def connection_factory(address, *, timeout):
        observed["connection"] = (address, timeout)
        return FakePlain()
    monkeypatch.setattr(ssl, "create_default_context", context_factory)
    monkeypatch.setattr(socket, "create_connection", connection_factory)
    result = probe(config, explicitly_disposable=True)
    assert observed["context"] == (ssl.Purpose.SERVER_AUTH, config.ca_file)
    assert observed["connection"] == ((config.host, config.port), config.timeout_seconds)
    assert result == {"mtls_handshake_verified": True, "admission_request_sent": False,
                      "dist01_certified": False, "dist08_certified": False}


def test_remote_tls_socket_timeout_fails_closed_without_admission(tmp_path, monkeypatch):
    import socket
    class FakePlain:
        def __enter__(self): return self
        def __exit__(self, *args): return False
    class FakeSecure:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def settimeout(self, timeout):
            assert timeout == 2.0
            raise TimeoutError("TLS peer socket timeout setup failed")
        def getpeercert(self): pytest.fail("peer accepted after timeout failure")
        def sendall(self, *args): pytest.fail("admission transmitted after TLS timeout")
    class FakeContext:
        verify_mode = ssl.CERT_NONE
        check_hostname = False
        def load_cert_chain(self, *args): pass
        def wrap_socket(self, *args, **kwargs): return FakeSecure()
    monkeypatch.setattr(ssl, "create_default_context", lambda *a, **k: FakeContext())
    monkeypatch.setattr(socket, "create_connection", lambda *a, **k: FakePlain())
    with pytest.raises(DistributedAdmissionUnavailable, match="handshake failed"):
        probe(_config(tmp_path), explicitly_disposable=True)


def test_peer_certificate_read_failure_closes_without_admission(tmp_path, monkeypatch):
    import socket
    class FakePlain:
        def __enter__(self): return self
        def __exit__(self, *args): return False
    class FakeSecure:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def settimeout(self, timeout): assert timeout == 2.0
        def getpeercert(self): raise ssl.SSLError("peer certificate read failed")
        def send(self, *args): pytest.fail("admission data sent")
        def sendall(self, *args): pytest.fail("admission data sent")
        def recv(self, *args): pytest.fail("admission data received")
    class FakeContext:
        verify_mode = ssl.CERT_NONE
        check_hostname = False
        def load_cert_chain(self, *args): pass
        def wrap_socket(self, *args, **kwargs): return FakeSecure()
    monkeypatch.setattr(ssl, "create_default_context", lambda *a, **k: FakeContext())
    monkeypatch.setattr(socket, "create_connection", lambda *a, **k: FakePlain())
    with pytest.raises(DistributedAdmissionUnavailable, match="handshake failed"):
        probe(_config(tmp_path), explicitly_disposable=True)
