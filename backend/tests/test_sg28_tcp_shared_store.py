"""Single-host TCP smoke tests for SG28 client transport; NOT multi-host proof."""
import json
import socketserver
import threading

import pytest

from app.services.sg28_tcp_shared_store import TcpSharedLeaseStore
from app.services.shared_admission_contract import (
    SharedAdmissionClient, SharedAdmissionUnavailable, SharedAdmissionRejected,
)


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        request = json.loads(self.rfile.readline())
        response = self.server.responder(request)
        if isinstance(response, bytes):
            self.wfile.write(response)
        elif response is not None:
            self.wfile.write((json.dumps(response) + "\n").encode())


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def serve(responder):
    server = Server(("127.0.0.1", 0), Handler)
    server.responder = responder
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def test_tcp_store_accepts_valid_lease_and_release():
    requests = []

    def respond(message):
        requests.append(message)
        if message["op"] == "grant":
            return {"granted": True, "owner": "worker-a", "generation": 1, "deadline": 5.0}
        return {"released": True}

    server, thread = serve(respond)
    try:
        client = SharedAdmissionClient(TcpSharedLeaseStore("127.0.0.1", server.server_address[1]))
        lease = client.acquire("worker-a", 5)
        assert (lease.owner, lease.generation, lease.deadline) == ("worker-a", 1, 5)
        assert client.release(lease) is True
        assert requests == [
            {"op": "grant", "owner": "worker-a", "ttl": 5},
            {"op": "release", "owner": "worker-a", "generation": 1},
        ]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


@pytest.mark.parametrize("reply,expected", [
    (None, SharedAdmissionUnavailable),
    ({"granted": True, "owner": "wrong", "generation": 1, "deadline": 5}, SharedAdmissionUnavailable),
    ({"granted": True, "owner": "a", "generation": 0, "deadline": 5}, SharedAdmissionUnavailable),
    ({"granted": True, "owner": "a", "generation": 1, "deadline": True}, SharedAdmissionUnavailable),
    ({"granted": True, "owner": "a", "generation": 1, "deadline": False}, SharedAdmissionUnavailable),
    ({"granted": False}, SharedAdmissionRejected),
    ({"error": "offline", "granted": False}, SharedAdmissionUnavailable),
    ({"unexpected": 1}, SharedAdmissionUnavailable),
    ({"granted": True, "error": "coordinator unavailable", "owner": "a", "generation": 1, "deadline": 5}, SharedAdmissionUnavailable),
    ({"granted": True, "error": None, "owner": "a", "generation": 1, "deadline": 5}, SharedAdmissionUnavailable),
])
def test_tcp_store_fails_closed_on_missing_or_invalid_ack(reply, expected):
    server, thread = serve(lambda _: reply)
    try:
        client = SharedAdmissionClient(TcpSharedLeaseStore("127.0.0.1", server.server_address[1]))
        with pytest.raises(expected):
            client.acquire("a", 5)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


@pytest.mark.parametrize("raw_reply", [
    b'{"granted":false,"granted":true,"owner":"a","generation":1,"deadline":5}\n',
    b'{"granted":true,"owner":"a","generation":1,"generation":2,"deadline":5}\n',
    b'{"granted":true,"owner":"a","generation":1,"deadline":NaN}\n',
    b'{"granted":true,"owner":"a","generation":1,"deadline":Infinity}\n',
])
def test_tcp_store_rejects_ambiguous_or_nonfinite_raw_ack(raw_reply):
    server, thread = serve(lambda _: raw_reply)
    try:
        client = SharedAdmissionClient(TcpSharedLeaseStore("127.0.0.1", server.server_address[1]))
        with pytest.raises(SharedAdmissionUnavailable):
            client.acquire("a", 5)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


@pytest.mark.parametrize("raw_reply", [
    b'{"granted":true,"owner":"a","generation":1,"deadline":5}',
    b'{"granted":true,"owner":"a","generation":1,"deadline":5}' + b" " * 8192 + b"\n",
])
def test_tcp_store_rejects_unterminated_or_oversized_ack(raw_reply):
    server, thread = serve(lambda _: raw_reply)
    try:
        client = SharedAdmissionClient(TcpSharedLeaseStore("127.0.0.1", server.server_address[1]))
        with pytest.raises(SharedAdmissionUnavailable):
            client.acquire("a", 5)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


@pytest.mark.parametrize("ack", [
    {"released": True, "error": "coordinator failure"},
    {"released": False, "error": None},
])
def test_tcp_store_rejects_contradictory_release_ack(ack):
    server, thread = serve(lambda _: ack)
    try:
        client = SharedAdmissionClient(TcpSharedLeaseStore("127.0.0.1", server.server_address[1]))
        from app.services.shared_admission_contract import SharedLease
        with pytest.raises(SharedAdmissionUnavailable):
            client.release(SharedLease("a", 1, 5))
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
