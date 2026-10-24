"""SG28 distinct spawned clients and coordinator communicate over mTLS on one host.

This is a CI-host multiprocessing characterization, NOT two independent hosts.
"""
import multiprocessing
import os
import shutil
import ssl
import subprocess
import threading
from concurrent.futures import ProcessPoolExecutor

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


def _client(port, server_cert, client_cert, client_key, barrier):
    exchange = make_mtls_exchange(CoordinatorTLSConfig(
        "127.0.0.1", port, "localhost", server_cert, client_cert, client_key,
    ))
    barrier.wait(timeout=15)
    return os.getpid(), exchange({"op": "grant"})


def _coordinator(db, server_cert, server_key, client_ca, port_sender, stop):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(server_cert, server_key)
    context.load_verify_locations(cafile=client_ca)
    context.verify_mode = ssl.CERT_REQUIRED
    with DisposableMTLSLeaseServer(
        ("127.0.0.1", 0), ssl_context=context,
        store=SQLiteLeaseStore(db, ttl=10),
        allowed_identities={"client-a", "client-b"},
        clock=lambda: 100,
    ) as server:
        port_sender.send(server.server_address[1])
        port_sender.close()
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            stop.wait(timeout=25)
        finally:
            server.shutdown()
            worker.join(timeout=5)


@pytest.mark.skipif(shutil.which("openssl") is None, reason="openssl unavailable")
def test_spawned_mtls_clients_share_k1_across_distinct_pids(tmp_path):
    server_cert, server_key = _cert(tmp_path, "localhost")
    first_cert, first_key = _cert(tmp_path, "client-a")
    second_cert, second_key = _cert(tmp_path, "client-b")
    bundle = tmp_path / "clients.pem"
    bundle.write_bytes(
        (tmp_path / "client-a.crt").read_bytes()
        + (tmp_path / "client-b.crt").read_bytes()
    )
    ctx = multiprocessing.get_context("spawn")
    with ctx.Manager() as manager:
        receiver, sender = ctx.Pipe(duplex=False)
        stop = manager.Event()
        coordinator = ctx.Process(
            target=_coordinator,
            args=(
                str(tmp_path / "shared.sqlite"),
                server_cert, server_key, str(bundle), sender, stop,
            ),
        )
        coordinator.start()
        sender.close()
        try:
            assert receiver.poll(15), "coordinator did not publish its port"
            port = receiver.recv()
            receiver.close()
            barrier = manager.Barrier(2)
            with ProcessPoolExecutor(max_workers=2, mp_context=ctx) as pool:
                futures = [
                    pool.submit(
                        _client, port, server_cert, cert, key, barrier,
                    )
                    for cert, key in ((first_cert, first_key), (second_cert, second_key))
                ]
                results = [future.result(timeout=20) for future in futures]
            assert len({pid for pid, _ in results}) == 2
            assert coordinator.pid not in {pid for pid, _ in results}
            winners = [reply for _, reply in results if reply.get("granted") is True]
            assert winners == [{"granted": True, "generation": 1}]
            assert sum(reply == {"granted": False, "generation": None} for _, reply in results) == 1
        finally:
            stop.set()
            coordinator.join(timeout=10)
            if coordinator.is_alive():
                coordinator.terminate()
                coordinator.join(timeout=5)
            assert coordinator.exitcode == 0
