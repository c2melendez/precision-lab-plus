"""SG28 isolated lost-ack integration with real TLS and persistent leases."""
import json
import shutil
import ssl
import subprocess
import threading

import pytest

from app.services.distributed_admission import (
    DistributedAdmissionUnavailable, acquire_distributed_admission,
)
from app.services.distributed_tls_transport import CoordinatorTLSConfig, make_mtls_exchange
from app.services.sg28_disposable_mtls_coordinator import DisposableMTLSLeaseServer, _LeaseHandler
from app.services.sg28_sqlite_lease_store import SQLiteLeaseStore


def _cert(tmp, name):
    cert, key = tmp / f"{name}.crt", tmp / f"{name}.key"
    subprocess.run(
        ["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
         "-days", "1", "-subj", f"/CN={name}",
         "-keyout", str(key), "-out", str(cert)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15,
    )
    return str(cert), str(key)


@pytest.mark.skipif(shutil.which("openssl") is None, reason="openssl unavailable")
def test_mtls_lost_grant_and_release_ack_preserve_fencing(tmp_path, monkeypatch):
    server_cert, server_key = _cert(tmp_path, "localhost")
    client_cert, client_key = _cert(tmp_path, "client-a")
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(server_cert, server_key)
    context.load_verify_locations(cafile=client_cert)
    context.verify_mode = ssl.CERT_REQUIRED
    store = SQLiteLeaseStore(str(tmp_path / "leases.sqlite"), ttl=10)
    now = {"value": 100}
    monkeypatch.setenv("SG28_DISTRIBUTED_ADMISSION", "1")

    class DropAckHandler(_LeaseHandler):
        def handle(self):
            # One-shot injected fault occurs *after* persistent mutation.
            request_line = self.rfile.readline(4097)
            identity = "client-a"  # Subject is checked by mTLS and server allowlist.
            peer = self.request.getpeercert()
            names = [v for group in peer.get("subject", ()) for k, v in group if k == "commonName"]
            if names != [identity] or not request_line.endswith(b"\n"):
                return
            payload = json.loads(request_line)
            if payload == {"op": "grant"} and self.server.drop_grant:
                self.server.drop_grant = False
                self.server.store.acquire(identity, now=self.server.clock())
                return
            if payload.get("op") == "release" and self.server.drop_release:
                self.server.drop_release = False
                self.server.store.release(identity, payload["generation"])
                return
            # For the remaining requests, replay the consumed frame through
            # the regular coordinator protocol rather than bypassing identity.
            if payload == {"op": "grant"}:
                lease = self.server.store.acquire(identity, now=self.server.clock())
                response = {"granted": bool(lease), "generation": lease.generation if lease else None}
            elif payload.get("op") == "release":
                response = {"released": self.server.store.release(identity, payload["generation"])}
            else:
                response = {"error": "unsupported operation"}
            self.wfile.write((json.dumps(response) + "\n").encode())

    with DisposableMTLSLeaseServer(
        ("127.0.0.1", 0), ssl_context=context, store=store,
        allowed_identities={"client-a"}, clock=lambda: now["value"],
    ) as server:
        server.RequestHandlerClass = DropAckHandler
        server.drop_grant = True
        server.drop_release = False
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            exchange = make_mtls_exchange(CoordinatorTLSConfig(
                "127.0.0.1", server.server_address[1],
                "localhost", server_cert, client_cert, client_key,
            ))
            with pytest.raises(DistributedAdmissionUnavailable):
                acquire_distributed_admission(exchange)
            assert store.acquire("third", now=101) is None
            with pytest.raises(DistributedAdmissionUnavailable):
                acquire_distributed_admission(exchange)

            now["value"] = 110
            assert acquire_distributed_admission(exchange).generation == 2
            server.drop_release = True
            with pytest.raises(DistributedAdmissionUnavailable):
                exchange({"op": "release", "generation": 2})
            assert acquire_distributed_admission(exchange).generation == 3
            assert exchange({"op": "release", "generation": 2}) == {"released": False}
            assert store.acquire("third", now=111) is None
        finally:
            server.shutdown()
            thread.join(timeout=5)
