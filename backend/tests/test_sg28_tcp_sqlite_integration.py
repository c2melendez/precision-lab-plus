"""Disposable loopback TCP + durable SQLite integration. NOT multi-host DIST proof."""
import json
from contextlib import closing
import socketserver
import threading

from app.services.sg28_sqlite_lease_reference import SqliteLeaseReference
from app.services.sg28_tcp_shared_store import TcpSharedLeaseStore
from app.services.shared_admission_contract import SharedAdmissionClient


class _Handler(socketserver.StreamRequestHandler):
    def handle(self):
        message = json.loads(self.rfile.readline(8193))
        store = self.server.lease_store
        if message.get("op") == "grant":
            lease = store.acquire(message["owner"], message["ttl"])
            response = {"granted": False} if lease is None else {
                "granted": True, "owner": lease.owner,
                "generation": lease.generation, "deadline": lease.deadline,
            }
        elif message.get("op") == "release":
            # Deadline comes from the persisted coordinator record, not client input.
            with closing(store._connect()) as conn:
                row = conn.execute(
                    "SELECT owner,generation,deadline FROM lease_state WHERE slot=1"
                ).fetchone()
            from app.services.shared_admission_contract import SharedLease
            lease = SharedLease(message["owner"], message["generation"], row[2])
            response = {"released": store.release(lease)}
        else:
            response = {"error": "invalid operation"}
        self.wfile.write((json.dumps(response) + "\n").encode())


class _Server(socketserver.ThreadingTCPServer):
    request_queue_size = 16  # Eight simultaneous disposable loopback clients.
    allow_reuse_address = True
    daemon_threads = True


def test_tcp_client_against_persistent_loopback_sqlite_coordinator(tmp_path):
    now = [100.0]
    db_path = tmp_path / "tcp-leases.sqlite"
    coordinator = SqliteLeaseReference(db_path, lambda: now[0])
    server = _Server(("127.0.0.1", 0), _Handler)
    server.lease_store = coordinator
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        port = server.server_address[1]
        worker_a = SharedAdmissionClient(TcpSharedLeaseStore("127.0.0.1", port))
        worker_b = SharedAdmissionClient(TcpSharedLeaseStore("127.0.0.1", port))
        first = worker_a.acquire("worker-a", 5)
        from app.services.shared_admission_contract import SharedAdmissionRejected
        import pytest
        with pytest.raises(SharedAdmissionRejected):
            worker_b.acquire("worker-b", 5)
        server.lease_store = SqliteLeaseReference(db_path, lambda: now[0])
        with pytest.raises(SharedAdmissionRejected):
            worker_b.acquire("worker-b", 5)
        now[0] = 105.0
        second = worker_b.acquire("worker-b", 5)
        assert second.generation == first.generation + 1
        assert worker_a.release(first) is False
        with pytest.raises(SharedAdmissionRejected):
            worker_a.acquire("worker-a", 5)
        assert worker_b.release(second) is True
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def test_network_outage_fails_closed_and_restart_preserves_lease(tmp_path):
    """Loopback fault simulation only, NOT distributed DIST-03/DIST-04 proof."""
    import pytest
    from app.services.shared_admission_contract import (
        SharedAdmissionRejected, SharedAdmissionUnavailable,
    )

    now = [20.0]
    db_path = tmp_path / "outage.sqlite"
    first_server = _Server(("127.0.0.1", 0), _Handler)
    first_server.lease_store = SqliteLeaseReference(db_path, lambda: now[0])
    port = first_server.server_address[1]
    thread = threading.Thread(target=first_server.serve_forever, daemon=True)
    thread.start()
    client_a = SharedAdmissionClient(TcpSharedLeaseStore("127.0.0.1", port))
    client_b = SharedAdmissionClient(TcpSharedLeaseStore("127.0.0.1", port))
    try:
        lease = client_a.acquire("a", 5)
    finally:
        first_server.shutdown()
        first_server.server_close()
        thread.join(timeout=3)

    with pytest.raises(SharedAdmissionUnavailable):
        client_b.acquire("b", 5)

    restarted = _Server(("127.0.0.1", port), _Handler)
    restarted.lease_store = SqliteLeaseReference(db_path, lambda: now[0])
    second_thread = threading.Thread(target=restarted.serve_forever, daemon=True)
    second_thread.start()
    try:
        with pytest.raises(SharedAdmissionRejected):
            client_b.acquire("b", 5)
        now[0] = lease.deadline
        recovered = client_b.acquire("b", 5)
        assert recovered.generation == lease.generation + 1
        assert client_a.release(lease) is False
        assert client_b.release(recovered) is True
    finally:
        restarted.shutdown()
        restarted.server_close()
        second_thread.join(timeout=3)


def test_lost_grant_ack_denies_client_without_early_second_grant(tmp_path):
    """Loopback lost-ACK characterization: NOT independent-host DIST-02."""
    import pytest
    from app.services.shared_admission_contract import (
        SharedAdmissionRejected, SharedAdmissionUnavailable,
    )

    now = [30.0]
    db = tmp_path / "lost-ack.sqlite"
    store = SqliteLeaseReference(db, lambda: now[0])

    class DropGrantAckHandler(socketserver.StreamRequestHandler):
        def handle(self):
            message = json.loads(self.rfile.readline(8193))
            if message["op"] == "grant" and message["owner"] == "uncertain":
                store.acquire(message["owner"], message["ttl"])
                return  # Persisted grant, but close socket without ACK.
            lease = store.acquire(message["owner"], message["ttl"])
            response = {"granted": False} if lease is None else {
                "granted": True, "owner": lease.owner,
                "generation": lease.generation, "deadline": lease.deadline,
            }
            self.wfile.write((json.dumps(response) + "\n").encode())

    server = _Server(("127.0.0.1", 0), DropGrantAckHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        port = server.server_address[1]
        uncertain = SharedAdmissionClient(TcpSharedLeaseStore("127.0.0.1", port))
        other = SharedAdmissionClient(TcpSharedLeaseStore("127.0.0.1", port))
        with pytest.raises(SharedAdmissionUnavailable):
            uncertain.acquire("uncertain", 5)
        with pytest.raises(SharedAdmissionRejected):
            other.acquire("other", 5)
        now[0] = 35.0
        recovered = other.acquire("other", 5)
        assert recovered.generation == 2
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def test_competing_tcp_clients_receive_single_grant_under_concurrency(tmp_path):
    """Loopback concurrent K=1 characterization, NOT multi-host DIST-01."""
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    now = [200.0]
    server = _Server(("127.0.0.1", 0), _Handler)
    server.lease_store = SqliteLeaseReference(tmp_path / "tcp-race.sqlite", lambda: now[0])
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        from app.services.shared_admission_contract import SharedAdmissionRejected
        import pytest

        barrier = Barrier(8)
        port = server.server_address[1]

        def attempt(i):
            client = SharedAdmissionClient(TcpSharedLeaseStore("127.0.0.1", port, timeout=5))
            barrier.wait(timeout=10)
            try:
                return client.acquire(f"tcp-worker-{i}", 5)
            except SharedAdmissionRejected:
                return None

        with ThreadPoolExecutor(max_workers=8) as pool:
            grants = list(pool.map(attempt, range(8)))
        accepted = [lease for lease in grants if lease is not None]
        assert len(accepted) == 1
        assert accepted[0].generation == 1
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
