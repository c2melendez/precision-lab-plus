"""SG28 coordinator rejects a cryptographically trusted but unauthorized peer.

Disposable loopback only. Verifies transport authentication != admission authority.
"""
import shutil
import ssl
import subprocess
import threading

import pytest

from app.services.distributed_admission import DistributedAdmissionUnavailable
from app.services.distributed_tls_transport import CoordinatorTLSConfig, make_mtls_exchange
from app.services.sg28_disposable_mtls_coordinator import DisposableMTLSLeaseServer
from app.services.sg28_sqlite_lease_store import SQLiteLeaseStore


def _cert(root, name):
    cert, key = root / f"{name}.crt", root / f"{name}.key"
    subprocess.run(
        ["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
         "-days", "1", "-subj", f"/CN={name}",
         "-keyout", str(key), "-out", str(cert)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15,
    )
    return str(cert), str(key)


@pytest.mark.skipif(shutil.which("openssl") is None, reason="openssl unavailable")
def test_trusted_tls_certificate_not_in_allowlist_cannot_mutate_lease(tmp_path):
    server_cert, server_key = _cert(tmp_path, "localhost")
    trusted_cert, trusted_key = _cert(tmp_path, "allowed-client")
    rogue_cert, rogue_key = _cert(tmp_path, "rogue-client")
    bundle = tmp_path / "bundle.pem"
    bundle.write_bytes(
        (tmp_path / "allowed-client.crt").read_bytes()
        + (tmp_path / "rogue-client.crt").read_bytes()
    )
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(server_cert, server_key)
    context.load_verify_locations(cafile=str(bundle))
    context.verify_mode = ssl.CERT_REQUIRED
    db = str(tmp_path / "admission.sqlite")
    store = SQLiteLeaseStore(db, ttl=10)
    with DisposableMTLSLeaseServer(
        ("127.0.0.1", 0), ssl_context=context, store=store,
        allowed_identities={"allowed-client"}, clock=lambda: 100,
    ) as server:
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            def transport(cert, key):
                return make_mtls_exchange(CoordinatorTLSConfig(
                    "127.0.0.1", server.server_address[1],
                    "localhost", server_cert, cert, key,
                ))
            rogue = transport(rogue_cert, rogue_key)
            with pytest.raises(DistributedAdmissionUnavailable):
                # An unauthorized peer may complete mTLS, but cannot gain a lease.
                from app.services.distributed_admission import validate_grant
                validate_grant(rogue({"op": "grant"}))
            assert store.acquire("control", now=100).generation == 1
            assert store.release("control", 1)
            allowed = transport(trusted_cert, trusted_key)
            assert allowed({"op": "grant"}) == {"granted": True, "generation": 2}
            assert rogue({"op": "release", "generation": 2}) != {"released": True}
            assert store.acquire("control", now=100) is None
        finally:
            server.shutdown()
            worker.join(timeout=5)
