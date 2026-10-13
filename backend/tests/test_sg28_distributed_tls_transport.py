"""SG28 mTLS exchange tests run only on disposable loopback sockets."""
import json
import shutil
import socketserver
import ssl
import subprocess
import threading

import pytest

from app.services.distributed_admission import DistributedAdmissionUnavailable
from app.services.distributed_tls_transport import CoordinatorTLSConfig, make_mtls_exchange


def _certificate(tmp_path, name):
    cert, key = tmp_path / (name + ".crt"), tmp_path / (name + ".key")
    subprocess.run(
        ["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
         "-days", "1", "-subj", f"/CN={name}", "-keyout", str(key), "-out", str(cert)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15,
    )
    return str(cert), str(key)


class _Handler(socketserver.StreamRequestHandler):
    def handle(self):
        peer = self.request.getpeercert()
        assert peer is not None
        request = json.loads(self.rfile.readline())
        if request == {"op": "grant"}:
            response = {"granted": True, "generation": 9}
        elif request == {"op": "release", "generation": 9}:
            response = {"released": True}
        else:
            response = {"error": "unsupported"}
        self.wfile.write((json.dumps(response) + "\n").encode())


class _Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def get_request(self):
        conn, addr = super().get_request()
        try:
            return self.context.wrap_socket(conn, server_side=True), addr
        except BaseException:
            conn.close()
            raise


@pytest.mark.skipif(shutil.which("openssl") is None, reason="openssl CLI unavailable")
def test_authenticated_tls_exchange_grant_release_and_wrong_server(tmp_path):
    server_cert, server_key = _certificate(tmp_path, "localhost")
    client_cert, client_key = _certificate(tmp_path, "sg28-client")
    wrong_cert, _ = _certificate(tmp_path, "wrong-server")
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(server_cert, server_key)
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_verify_locations(cafile=client_cert)
    with _Server(("127.0.0.1", 0), _Handler) as server:
        server.context = context
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        config = CoordinatorTLSConfig(
            "127.0.0.1", server.server_address[1], "localhost",
            server_cert, client_cert, client_key,
        )
        try:
            exchange = make_mtls_exchange(config)
            assert exchange({"op": "grant"}) == {"granted": True, "generation": 9}
            assert exchange({"op": "release", "generation": 9}) == {"released": True}
            for invalid in (
                {"op": "grant", "owner": "spoofed"},
                {"op": "grant", "now": 9999999},
                {"op": "release", "generation": True},
                {"op": "release", "generation": -1},
            ):
                with pytest.raises(DistributedAdmissionUnavailable):
                    exchange(invalid)
            # Trusted CA alone is insufficient if the server hostname differs.
            wrong_hostname = CoordinatorTLSConfig(
                config.host, config.port, "other.staging.internal",
                server_cert, client_cert, client_key,
            )
            with pytest.raises(DistributedAdmissionUnavailable):
                make_mtls_exchange(wrong_hostname)({"op": "grant"})
            untrusted = CoordinatorTLSConfig(
                config.host, config.port, config.server_name,
                wrong_cert, client_cert, client_key,
            )
            with pytest.raises(DistributedAdmissionUnavailable):
                make_mtls_exchange(untrusted)({"op": "grant"})
        finally:
            server.shutdown()
            thread.join(timeout=5)


def test_tls_transport_requires_explicit_trust_files(tmp_path):
    config = CoordinatorTLSConfig(
        "127.0.0.1", 5000, "localhost",
        str(tmp_path / "not-a-ca"), "missing-client", "missing-key",
    )
    with pytest.raises(DistributedAdmissionUnavailable):
        make_mtls_exchange(config)


@pytest.mark.parametrize("timeout", [0, -1, 10.01, float("nan"), float("inf"),
                                     float("-inf"), True, False, "2", None])
def test_tls_transport_rejects_invalid_timeout_without_network(tmp_path, monkeypatch, timeout):
    import socket

    def forbidden_network(*args, **kwargs):
        raise AssertionError("invalid configuration attempted network access")

    monkeypatch.setattr(socket, "create_connection", forbidden_network)
    config = CoordinatorTLSConfig(
        "127.0.0.1", 5000, "localhost",
        str(tmp_path / "not-a-ca"), "missing-client", "missing-key", timeout,
    )
    with pytest.raises(DistributedAdmissionUnavailable, match="timeout"):
        make_mtls_exchange(config)
