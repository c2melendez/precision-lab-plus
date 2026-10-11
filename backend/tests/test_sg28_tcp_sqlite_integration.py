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
