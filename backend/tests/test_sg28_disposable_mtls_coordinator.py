"""Integration gate: disposable mTLS coordinator, SQL lease, real TLS client."""
import shutil
import ssl
import subprocess
import threading

import pytest

from app.services.distributed_admission import (
    DistributedAdmissionUnavailable,
    distributed_admission_lease,
)
from app.services.distributed_tls_transport import (
    CoordinatorTLSConfig, make_mtls_exchange,
)
from app.services.sg28_disposable_mtls_coordinator import DisposableMTLSLeaseServer
from app.services.sg28_sqlite_lease_store import SQLiteLeaseStore


def _cert(tmp_path, name):
    cert, key = tmp_path / f"{name}.crt", tmp_path / f"{name}.key"
    subprocess.run(
        ["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
         "-days", "1", "-subj", f"/CN={name}",
         "-keyout", str(key), "-out", str(cert)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15,
    )
    return str(cert), str(key)


@pytest.mark.skipif(shutil.which("openssl") is None, reason="openssl unavailable")
def test_disposable_mtls_coordinator_enforces_owner_k1_and_fenced_release(
    tmp_path, monkeypatch,
):
    server_cert, server_key = _cert(tmp_path, "localhost")
    client_a_cert, client_a_key = _cert(tmp_path, "client-a")
    client_b_cert, client_b_key = _cert(tmp_path, "client-b")

    # A test-only bundle with both trusted client certificates.
    client_bundle = tmp_path / "trusted-clients.pem"
    client_bundle.write_bytes(
        (tmp_path / "client-a.crt").read_bytes()
        + (tmp_path / "client-b.crt").read_bytes()
    )
    server_tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    server_tls.load_cert_chain(server_cert, server_key)
    server_tls.load_verify_locations(cafile=str(client_bundle))
    server_tls.verify_mode = ssl.CERT_REQUIRED

    now = {"value": 100.0}
    store = SQLiteLeaseStore(str(tmp_path / "leases.sqlite"), ttl=10)
    with DisposableMTLSLeaseServer(
        ("127.0.0.1", 0), ssl_context=server_tls, store=store,
        allowed_identities={"client-a", "client-b"},
        clock=lambda: now["value"],
    ) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            def transport(cert, key):
                config = CoordinatorTLSConfig(
                    "127.0.0.1", server.server_address[1],
                    "localhost", server_cert, cert, key,
                )
                return make_mtls_exchange(config)

            a = transport(client_a_cert, client_a_key)
            b = transport(client_b_cert, client_b_key)
            monkeypatch.setenv("SG28_DISTRIBUTED_ADMISSION", "1")
            with distributed_admission_lease(a) as grant:
                assert grant.generation == 1
                assert b({"op": "grant"}) == {
                    "granted": False, "generation": None
                }
                assert b({"op": "release", "generation": 1}) == {
                    "released": False
                }
            second = b({"op": "grant"})
            assert second == {"granted": True, "generation": 2}
            assert a({"op": "release", "generation": 1}) == {"released": False}
            assert b({"op": "release", "generation": 2}) == {"released": True}
            now["value"] = 101.0
            assert a({"op": "grant"}) == {"granted": True, "generation": 3}
        finally:
            server.shutdown()
            thread.join(timeout=5)
            assert not thread.is_alive()


def test_disposable_service_rejects_public_binding(tmp_path):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    with pytest.raises(ValueError, match="loopback"):
        DisposableMTLSLeaseServer(
            ("0.0.0.0", 0), ssl_context=context,
            store=SQLiteLeaseStore(str(tmp_path / "unused.sqlite")),
            allowed_identities={"client-a"},
        )
