"""SG28 mTLS coordinator contention with persistent K=1 on one CI host."""
import shutil
import ssl
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

from app.services.distributed_tls_transport import CoordinatorTLSConfig, make_mtls_exchange
from app.services.sg28_disposable_mtls_coordinator import DisposableMTLSLeaseServer
from app.services.sg28_sqlite_lease_store import SQLiteLeaseStore


def _cert(tmp, name):
    cert, key = tmp / f"{name}.crt", tmp / f"{name}.key"
    subprocess.run(
        ["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "1",
         "-subj", f"/CN={name}", "-keyout", str(key), "-out", str(cert)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15,
    )
    return str(cert), str(key)


@pytest.mark.skipif(shutil.which("openssl") is None, reason="openssl unavailable")
def test_mtls_concurrent_clients_only_one_global_lease_then_recover(tmp_path):
    server_cert, server_key = _cert(tmp_path, "localhost")
    clients = [_cert(tmp_path, f"client-{i}") for i in range(6)]
    trust = tmp_path / "trusted.pem"
    trust.write_bytes(b"".join(
        (tmp_path / f"client-{i}.crt").read_bytes() for i in range(6)
    ))
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(server_cert, server_key)
    context.load_verify_locations(cafile=str(trust))
    context.verify_mode = ssl.CERT_REQUIRED
    store = SQLiteLeaseStore(str(tmp_path / "leases.sqlite"), ttl=10)
    clock = {"now": 100}
    with DisposableMTLSLeaseServer(
        ("127.0.0.1", 0), ssl_context=context, store=store,
        allowed_identities={f"client-{i}" for i in range(6)},
        clock=lambda: clock["now"],
    ) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            barrier = threading.Barrier(6)

            def contend(index):
                cert, key = clients[index]
                exchange = make_mtls_exchange(CoordinatorTLSConfig(
                    "127.0.0.1", server.server_address[1],
                    "localhost", server_cert, cert, key,
                ))
                barrier.wait(timeout=10)
                return index, exchange({"op": "grant"})

            with ThreadPoolExecutor(max_workers=6) as pool:
                attempts = list(pool.map(contend, range(6)))
            winners = [(idx, result["generation"]) for idx, result in attempts
                       if result.get("granted") is True]
            assert len(winners) == 1
            assert winners[0][1] == 1
            assert sum(result.get("granted") is False for _, result in attempts) == 5

            clock["now"] = 110
            successor = next(i for i in range(6) if i != winners[0][0])
            cert, key = clients[successor]
            exchange = make_mtls_exchange(CoordinatorTLSConfig(
                "127.0.0.1", server.server_address[1],
                "localhost", server_cert, cert, key,
            ))
            assert exchange({"op": "grant"}) == {"granted": True, "generation": 2}
            old_cert, old_key = clients[winners[0][0]]
            old_exchange = make_mtls_exchange(CoordinatorTLSConfig(
                "127.0.0.1", server.server_address[1],
                "localhost", server_cert, old_cert, old_key,
            ))
            assert old_exchange({"op": "release", "generation": 1}) == {"released": False}
            assert exchange({"op": "release", "generation": 2}) == {"released": True}
        finally:
            server.shutdown()
            thread.join(timeout=5)
