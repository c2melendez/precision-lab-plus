"""SG28 test-only TCP admission fixture; not a production or multi-host coordinator."""
import json
import socket
import socketserver
import threading

import pytest

import sqlite3


def _connect(db):
    con = sqlite3.connect(db, timeout=5, isolation_level=None)
    con.execute("PRAGMA busy_timeout=5000")
    return con


def _grant(db, owner, now, ttl):
    con = _connect(db)
    try:
        con.execute("BEGIN IMMEDIATE")
        row = con.execute("SELECT owner, generation, deadline FROM active_lease WHERE id=1").fetchone()
        if row and now < row[2]:
            con.execute("COMMIT")
            return None
        generation = (row[1] if row else 0) + 1
        con.execute(
            "INSERT INTO active_lease(id, owner, generation, deadline) VALUES(1, ?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET owner=excluded.owner, "
            "generation=excluded.generation, deadline=excluded.deadline",
            (owner, generation, now + ttl),
        )
        con.execute("COMMIT")
        return generation
    finally:
        con.close()


def _release(db, owner, generation):
    con = _connect(db)
    try:
        con.execute("BEGIN IMMEDIATE")
        changed = con.execute(
            "UPDATE active_lease SET deadline=-1 WHERE id=1 AND owner=? "
            "AND generation=? AND deadline>=0", (owner, generation),
        ).rowcount
        con.execute("COMMIT")
        return bool(changed)
    finally:
        con.close()



class AdmissionHandler(socketserver.StreamRequestHandler):
    def handle(self):
        data = json.loads(self.rfile.readline().decode("utf-8"))
        if data["op"] == "grant":
            generation = _grant(self.server.db, data["owner"], data["now"], data["ttl"])
            response = {"granted": generation is not None, "generation": generation}
        elif data["op"] == "release":
            response = {"released": _release(self.server.db, data["owner"], data["generation"])}
        else:
            response = {"error": "unsupported operation"}
        self.wfile.write((json.dumps(response) + "\n").encode("utf-8"))


class AdmissionServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def request(port, payload):
    # Fail closed: a broken network connection never authorizes computation.
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=1.5) as conn:
            conn.settimeout(1.5)
            conn.sendall((json.dumps(payload) + "\n").encode("utf-8"))
            with conn.makefile("rb") as reply:
                data = reply.readline()
        if not data:
            return {"granted": False, "error": "coordinator disconnected"}
        return json.loads(data)
    except (OSError, ValueError, json.JSONDecodeError):
        return {"granted": False, "error": "coordinator unavailable"}


def test_network_admission_fails_closed_during_coordinator_outage_and_recovers(tmp_path):
    """Loopback TCP checks actual transport denial, outage, and fenced recovery."""
    db = str(tmp_path / "network-gate.sqlite")
    with _connect(db) as con:
        con.execute(
            "CREATE TABLE active_lease(id INTEGER PRIMARY KEY, "
            "owner TEXT NOT NULL, generation INTEGER NOT NULL, "
            "deadline REAL NOT NULL)"
        )
    with AdmissionServer(("127.0.0.1", 0), AdmissionHandler) as server:
        server.db = db
        port = server.server_address[1]
        task = threading.Thread(target=server.serve_forever, daemon=True)
        task.start()
        first = request(port, {"op": "grant", "owner": "a", "now": 0, "ttl": 5})
        assert first == {"granted": True, "generation": 1}
        assert request(port, {"op": "grant", "owner": "b", "now": 1, "ttl": 5})["granted"] is False
        server.shutdown()
        task.join(timeout=5)
    assert not task.is_alive()
    assert request(port, {"op": "grant", "owner": "b", "now": 5, "ttl": 5})["granted"] is False

    with AdmissionServer(("127.0.0.1", 0), AdmissionHandler) as replacement:
        replacement.db = db
        new_port = replacement.server_address[1]
        task = threading.Thread(target=replacement.serve_forever, daemon=True)
        task.start()
        try:
            assert request(new_port, {"op": "grant", "owner": "b", "now": 5, "ttl": 5}) == {"granted": True, "generation": 2}
            assert request(new_port, {"op": "release", "owner": "a", "generation": 1}) == {"released": False}
            assert request(new_port, {"op": "grant", "owner": "c", "now": 6, "ttl": 5})["granted"] is False
        finally:
            replacement.shutdown()
            task.join(timeout=5)
