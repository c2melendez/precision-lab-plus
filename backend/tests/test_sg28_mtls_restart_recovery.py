"""SG28 isolated mTLS coordinator restart and outage regressions (one CI host)."""
import shutil
import ssl
import subprocess
import threading

import pytest

from app.services.distributed_admission import (
    DistributedAdmissionUnavailable, acquire_distributed_admission,
)
from app.services.distributed_tls_transport import CoordinatorTLSConfig, make_mtls_exchange
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
def test_mtls_restart_keeps_lease_fenced_and_recovers_after_expiry(tmp_path, monkeypatch):
    server_cert, server_key = _cert(tmp_path, "localhost")
    client_a_cert, client_a_key = _cert(tmp_path, "client-a")
    client_b_cert, client_b_key = _cert(tmp_path, "client-b")
    bundle = tmp_path / "clients.pem"
    bundle.write_bytes(
        (tmp_path / "client-a.crt").read_bytes()
        + (tmp_path / "client-b.crt").read_bytes()
    )
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(server_cert, server_key)
    context.load_verify_locations(cafile=str(bundle))
    context.verify_mode = ssl.CERT_REQUIRED
    db = str(tmp_path / "restart.sqlite")
    clock = {"value": 100}
    monkeypatch.setenv("SG28_DISTRIBUTED_ADMISSION", "1")

    def serve():
        service = DisposableMTLSLeaseServer(
            ("127.0.0.1", 0), ssl_context=context,
            store=SQLiteLeaseStore(db, ttl=10),
            allowed_identities={"client-a", "client-b"},
            clock=lambda: clock["value"],
        )
        thread = threading.Thread(target=service.serve_forever, daemon=True)
        thread.start()
        return service, thread

    def client(port, cert, key):
        return make_mtls_exchange(CoordinatorTLSConfig(
            "127.0.0.1", port, "localhost", server_cert, cert, key,
        ))

    first, worker = serve()
    port = first.server_address[1]
    original = client(port, client_a_cert, client_a_key)
    try:
        assert acquire_distributed_admission(original).generation == 1
    finally:
        first.shutdown()
        first.server_close()
        worker.join(timeout=5)
    assert not worker.is_alive()

    # The old transport is dead: failure must not be treated as authorization.
    with pytest.raises(DistributedAdmissionUnavailable):
        acquire_distributed_admission(original)

    restored, worker = serve()
    try:
        contender = client(restored.server_address[1], client_b_cert, client_b_key)
        with pytest.raises(DistributedAdmissionUnavailable):
            acquire_distributed_admission(contender)
        clock["value"] = 110
        assert acquire_distributed_admission(contender).generation == 2
        updated = client(restored.server_address[1], client_a_cert, client_a_key)
        assert updated({"op": "release", "generation": 1}) == {"released": False}
        with pytest.raises(DistributedAdmissionUnavailable):
            acquire_distributed_admission(updated)
        assert contender({"op": "release", "generation": 2}) == {"released": True}
        assert acquire_distributed_admission(updated).generation == 3
    finally:
        restored.shutdown()
        restored.server_close()
        worker.join(timeout=5)
    assert not worker.is_alive()
