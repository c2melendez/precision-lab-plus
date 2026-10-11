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
        if data["op"] == "grant_disconnect":
            # Commit the grant but intentionally lose the acknowledgement.
            _grant(self.server.db, data["owner"], data["now"], data["ttl"])
            return
        if data["op"] == "grant":
            generation = _grant(self.server.db, data["owner"], data["now"], data["ttl"])
            response = {"granted": generation is not None, "generation": generation}
        elif data["op"] == "release_disconnect":
            _release(self.server.db, data["owner"], data["generation"])
            return
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


def _coordinator_process(db, ready, stop):
    """Independent spawned coordinator, using only disposable loopback TCP."""
    with AdmissionServer(("127.0.0.1", 0), AdmissionHandler) as server:
        server.db = db
        ready.send(server.server_address[1])
        ready.close()
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            stop.wait(timeout=20)
        finally:
            server.shutdown()
            thread.join(timeout=5)


def _independent_client(port, owner, barrier):
    import os
    barrier.wait(timeout=10)
    result = request(port, {"op": "grant", "owner": owner, "now": 0, "ttl": 5})
    return os.getpid(), owner, result


def test_spawned_coordinator_and_distinct_clients_enforce_network_k1(tmp_path):
    """Separate PIDs traverse real TCP and exactly one client receives K=1."""
    import multiprocessing
    from concurrent.futures import ProcessPoolExecutor

    db = str(tmp_path / "independent-tcp.sqlite")
    with _connect(db) as con:
        con.execute(
            "CREATE TABLE active_lease(id INTEGER PRIMARY KEY, "
            "owner TEXT NOT NULL, generation INTEGER NOT NULL, "
            "deadline REAL NOT NULL)"
        )
    ctx = multiprocessing.get_context("spawn")
    with ctx.Manager() as manager:
        stop = manager.Event()
        receiver, sender = ctx.Pipe(duplex=False)
        coordinator = ctx.Process(target=_coordinator_process, args=(db, sender, stop))
        coordinator.start()
        sender.close()
        try:
            assert receiver.poll(15), "coordinator did not publish its port"
            port = receiver.recv()
            receiver.close()
            barrier = manager.Barrier(2)
            with ProcessPoolExecutor(max_workers=2, mp_context=ctx) as pool:
                futures = [
                    pool.submit(_independent_client, port, owner, barrier)
                    for owner in ("client-a", "client-b")
                ]
                results = [future.result(timeout=20) for future in futures]
            assert len({pid for pid, _, _ in results}) == 2
            assert coordinator.pid not in {pid for pid, _, _ in results}
            winners = [(owner, value["generation"]) for _, owner, value in results if value["granted"]]
            assert len(winners) == 1
            assert winners[0][1] == 1
            assert request(port, {"op": "grant", "owner": "third", "now": 1, "ttl": 5})["granted"] is False
        finally:
            stop.set()
            coordinator.join(timeout=10)
            if coordinator.is_alive():
                coordinator.terminate()
                coordinator.join(timeout=5)
            assert coordinator.exitcode == 0


def test_abrupt_tcp_coordinator_process_death_fails_closed_and_fences_restart(tmp_path):
    """K=1 persists after coordinator SIGTERM; no admission during outage."""
    import multiprocessing

    db = str(tmp_path / "coordinator-crash.sqlite")
    with _connect(db) as con:
        con.execute(
            "CREATE TABLE active_lease(id INTEGER PRIMARY KEY, "
            "owner TEXT NOT NULL, generation INTEGER NOT NULL, "
            "deadline REAL NOT NULL)"
        )
    ctx = multiprocessing.get_context("spawn")
    with ctx.Manager() as manager:
        stop = manager.Event()
        receiver, sender = ctx.Pipe(duplex=False)
        coordinator = ctx.Process(target=_coordinator_process, args=(db, sender, stop))
        coordinator.start()
        sender.close()
        try:
            assert receiver.poll(15), "coordinator failed to start"
            port = receiver.recv()
            assert request(port, {"op": "grant", "owner": "first", "now": 0, "ttl": 5}) == {
                "granted": True, "generation": 1
            }
            coordinator.terminate()
            coordinator.join(timeout=10)
            assert not coordinator.is_alive()
            assert request(port, {"op": "grant", "owner": "second", "now": 5, "ttl": 5})["granted"] is False
        finally:
            receiver.close()
            if coordinator.is_alive():
                coordinator.terminate()
                coordinator.join(timeout=5)

        with AdmissionServer(("127.0.0.1", 0), AdmissionHandler) as restored:
            restored.db = db
            replacement_port = restored.server_address[1]
            thread = threading.Thread(target=restored.serve_forever, daemon=True)
            thread.start()
            try:
                assert request(replacement_port, {"op": "grant", "owner": "second", "now": 4, "ttl": 5})["granted"] is False
                assert request(replacement_port, {"op": "grant", "owner": "second", "now": 5, "ttl": 5}) == {
                    "granted": True, "generation": 2
                }
                assert request(replacement_port, {"op": "release", "owner": "first", "generation": 1}) == {
                    "released": False
                }
            finally:
                restored.shutdown()
                thread.join(timeout=5)


def test_lost_grant_acknowledgement_fails_closed_and_preserves_fencing(tmp_path):
    """A committed grant with dropped TCP reply must never count as client admission."""
    db = str(tmp_path / "lost-ack.sqlite")
    with _connect(db) as con:
        con.execute(
            "CREATE TABLE active_lease(id INTEGER PRIMARY KEY, "
            "owner TEXT NOT NULL, generation INTEGER NOT NULL, "
            "deadline REAL NOT NULL)"
        )
    with AdmissionServer(("127.0.0.1", 0), AdmissionHandler) as server:
        server.db = db
        port = server.server_address[1]
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            uncertain = request(port, {
                "op": "grant_disconnect", "owner": "lost-ack", "now": 0, "ttl": 5
            })
            assert uncertain["granted"] is False
            with _connect(db) as con:
                assert con.execute(
                    "SELECT owner, generation, deadline FROM active_lease WHERE id=1"
                ).fetchone() == ("lost-ack", 1, 5)
            assert request(port, {
                "op": "grant", "owner": "another", "now": 1, "ttl": 5
            })["granted"] is False
            assert request(port, {
                "op": "grant", "owner": "another", "now": 5, "ttl": 5
            }) == {"granted": True, "generation": 2}
            assert request(port, {
                "op": "release", "owner": "lost-ack", "generation": 1
            }) == {"released": False}
        finally:
            server.shutdown()
            thread.join(timeout=5)


def test_tcp_duplicate_retry_after_lost_ack_remains_unadmitted(tmp_path):
    """Retry of a grant whose reply was lost must not bypass active K=1 lease."""
    db = str(tmp_path / "retry-after-lost-ack.sqlite")
    with _connect(db) as con:
        con.execute(
            "CREATE TABLE active_lease(id INTEGER PRIMARY KEY, "
            "owner TEXT NOT NULL, generation INTEGER NOT NULL, "
            "deadline REAL NOT NULL)"
        )
    with AdmissionServer(("127.0.0.1", 0), AdmissionHandler) as server:
        server.db = db
        port = server.server_address[1]
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            first = request(port, {
                "op": "grant_disconnect", "owner": "worker-a", "now": 0, "ttl": 5
            })
            assert first["granted"] is False
            retry = request(port, {
                "op": "grant", "owner": "worker-a", "now": 1, "ttl": 5
            })
            assert retry["granted"] is False
            assert request(port, {
                "op": "grant", "owner": "worker-b", "now": 2, "ttl": 5
            })["granted"] is False
            assert request(port, {
                "op": "grant", "owner": "worker-a", "now": 5, "ttl": 5
            }) == {"granted": True, "generation": 2}
            assert request(port, {
                "op": "release", "owner": "worker-a", "generation": 1
            }) == {"released": False}
        finally:
            server.shutdown()
            thread.join(timeout=5)


def test_tcp_lost_release_ack_does_not_revoke_successor(tmp_path):
    """A repeated release following a dropped reply must not evict a later lease."""
    db = str(tmp_path / "release-ack.sqlite")
    with _connect(db) as con:
        con.execute(
            "CREATE TABLE active_lease(id INTEGER PRIMARY KEY, "
            "owner TEXT NOT NULL, generation INTEGER NOT NULL, "
            "deadline REAL NOT NULL)"
        )
    with AdmissionServer(("127.0.0.1", 0), AdmissionHandler) as server:
        server.db = db
        port = server.server_address[1]
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            assert request(port, {"op": "grant", "owner": "first", "now": 0, "ttl": 5}) == {
                "granted": True, "generation": 1
            }
            assert request(port, {"op": "release", "owner": "first", "generation": 1}) == {
                "released": True
            }
            assert request(port, {"op": "grant", "owner": "second", "now": 1, "ttl": 5}) == {
                "granted": True, "generation": 2
            }
            # Model a client resending release because its previous reply was lost.
            assert request(port, {"op": "release", "owner": "first", "generation": 1}) == {
                "released": False
            }
            assert request(port, {"op": "grant", "owner": "third", "now": 2, "ttl": 5})["granted"] is False
            with _connect(db) as con:
                assert con.execute(
                    "SELECT owner, generation, deadline FROM active_lease WHERE id=1"
                ).fetchone() == ("second", 2, 6)
        finally:
            server.shutdown()
            thread.join(timeout=5)


def test_tcp_lost_release_ack_retry_remains_fenced(tmp_path):
    """Commit release but drop reply; duplicate retry cannot evict successor."""
    db = str(tmp_path / "lost-release-ack.sqlite")
    with _connect(db) as con:
        con.execute(
            "CREATE TABLE active_lease(id INTEGER PRIMARY KEY, "
            "owner TEXT NOT NULL, generation INTEGER NOT NULL, "
            "deadline REAL NOT NULL)"
        )
    with AdmissionServer(("127.0.0.1", 0), AdmissionHandler) as server:
        server.db = db
        port = server.server_address[1]
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            assert request(port, {"op": "grant", "owner": "first", "now": 0, "ttl": 5}) == {
                "granted": True, "generation": 1
            }
            uncertain = request(port, {
                "op": "release_disconnect", "owner": "first", "generation": 1
            })
            assert uncertain["granted"] is False
            assert request(port, {"op": "grant", "owner": "second", "now": 1, "ttl": 5}) == {
                "granted": True, "generation": 2
            }
            assert request(port, {"op": "release", "owner": "first", "generation": 1}) == {
                "released": False
            }
            assert request(port, {"op": "grant", "owner": "third", "now": 2, "ttl": 5})["granted"] is False
            with _connect(db) as con:
                assert con.execute(
                    "SELECT owner, generation, deadline FROM active_lease WHERE id=1"
                ).fetchone() == ("second", 2, 6)
        finally:
            server.shutdown()
            thread.join(timeout=5)


def test_tcp_unknown_release_response_keeps_client_fail_closed(tmp_path):
    """A malformed response must never be treated as successful admission."""
    db = str(tmp_path / "unknown-response.sqlite")
    with _connect(db) as con:
        con.execute(
            "CREATE TABLE active_lease(id INTEGER PRIMARY KEY, "
            "owner TEXT NOT NULL, generation INTEGER NOT NULL, "
            "deadline REAL NOT NULL)"
        )
    with AdmissionServer(("127.0.0.1", 0), AdmissionHandler) as server:
        server.db = db
        port = server.server_address[1]
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            assert request(port, {
                "op": "grant", "owner": "first", "now": 0, "ttl": 5
            }) == {"granted": True, "generation": 1}
            invalid = request(port, {"op": "unsupported"})
            assert invalid.get("granted", False) is False
            assert invalid == {"error": "unsupported operation"}
            assert request(port, {
                "op": "grant", "owner": "second", "now": 1, "ttl": 5
            })["granted"] is False
        finally:
            server.shutdown()
            thread.join(timeout=5)
