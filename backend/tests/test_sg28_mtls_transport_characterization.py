"""SG28 test-only mutual TLS handshake characterization on loopback.

No real coordinator, production secrets, or multi-host certification is claimed.
Certificates are generated inside tmp_path and discarded after pytest.
"""
import json
import shutil
import socket
import socketserver
import ssl
import subprocess
import threading

import pytest


def _self_signed(tmp_path, name):
    key = tmp_path / f"{name}.key"
    cert = tmp_path / f"{name}.crt"
    subprocess.run(
        [
            "openssl", "req", "-x509", "-newkey", "rsa:2048",
            "-nodes", "-days", "1", "-sha256",
            "-subj", f"/CN={name}",
            "-keyout", str(key), "-out", str(cert),
        ],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        timeout=15,
    )
    return cert, key


class _MutualTLSHandler(socketserver.StreamRequestHandler):
    def handle(self):
        # This authenticated principal is derived from peer TLS identity,
        # never from user-provided JSON fields.
        peer = self.request.getpeercert()
        common_names = [
            value for group in peer["subject"]
            for key, value in group if key == "commonName"
        ]
        if common_names != ["sg28-client"]:
            self.wfile.write(b'{"error":"unauthorized"}\n')
            return
        payload = json.loads(self.rfile.readline())
        self.wfile.write(
            (json.dumps({"authenticated": True, "owner": common_names[0]}) + "\n").encode()
        )


class _MutualTLSServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def get_request(self):
        sock, address = super().get_request()
        try:
            return self.tls_context.wrap_socket(sock, server_side=True), address
        except BaseException:
            sock.close()
            raise


def _client_context(server_cert, client_cert=None, client_key=None):
    context = ssl.create_default_context(cafile=str(server_cert))
    if client_cert is not None:
        context.load_cert_chain(str(client_cert), str(client_key))
    return context


def _exchange(port, context):
    with socket.create_connection(("127.0.0.1", port), timeout=2) as raw:
        with context.wrap_socket(raw, server_hostname="localhost") as conn:
            conn.settimeout(2)
            conn.sendall(b'{"op":"grant","owner":"spoofed"}\n')
            return conn.recv(4096)


@pytest.mark.skipif(shutil.which("openssl") is None, reason="openssl CLI unavailable")
def test_mtls_requires_trusted_client_and_verified_server_identity(tmp_path):
    """Unauthenticated and untrusted peers cannot exchange admission requests."""
    server_cert, server_key = _self_signed(tmp_path, "localhost")
    client_cert, client_key = _self_signed(tmp_path, "sg28-client")
    rogue_cert, rogue_key = _self_signed(tmp_path, "rogue-client")

    server_tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    server_tls.load_cert_chain(str(server_cert), str(server_key))
    server_tls.verify_mode = ssl.CERT_REQUIRED
    server_tls.load_verify_locations(cafile=str(client_cert))

    with _MutualTLSServer(("127.0.0.1", 0), _MutualTLSHandler) as server:
        server.tls_context = server_tls
        port = server.server_address[1]
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            valid = _exchange(
                port, _client_context(server_cert, client_cert, client_key)
            )
            assert json.loads(valid) == {
                "authenticated": True, "owner": "sg28-client"
            }

            # The server requires a client certificate before accepting data.
            try:
                missing_client_reply = _exchange(port, _client_context(server_cert))
            except (ssl.SSLError, ConnectionError, OSError):
                missing_client_reply = b""
            assert missing_client_reply == b""

            # A certificate not trusted by the server must not receive data.
            try:
                rogue_client_reply = _exchange(
                    port, _client_context(server_cert, rogue_cert, rogue_key)
                )
            except (ssl.SSLError, ConnectionError, OSError):
                rogue_client_reply = b""
            assert rogue_client_reply == b""

            # The client must reject the wrong server trust anchor.
            with pytest.raises(ssl.SSLError):
                _exchange(
                    port, _client_context(rogue_cert, client_cert, client_key)
                )
        finally:
            server.shutdown()
            worker.join(timeout=5)
            assert not worker.is_alive()
