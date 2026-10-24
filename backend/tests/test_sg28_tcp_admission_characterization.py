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
        result = json.loads(data)
        # A remote coordinator's reply is untrusted. Never treat an incomplete,
        # forged, or wrongly typed grant as authorization to start computation.
        if not isinstance(result, dict):
            return {"granted": False, "error": "invalid coordinator response"}
        if result.get("granted") is True:
            generation = result.get("generation")
            if (payload.get("op") != "grant"
                    or set(result) != {"granted", "generation"}
                    or type(generation) is not int or generation < 1):
                return {"granted": False, "error": "invalid coordinator grant"}
        elif result.get("granted") is False:
            if (payload.get("op") not in ("grant", "grant_disconnect")
                    or set(result) != {"granted", "generation"}
                    or result.get("generation") is not None):
                return {"granted": False, "error": "unexpected coordinator response"}
        elif type(result.get("released")) is bool:
            if payload.get("op") not in ("release", "release_disconnect") or set(result) != {"released"}:
                return {"granted": False, "error": "unexpected coordinator response"}
        elif isinstance(result.get("error"), str):
            if set(result) != {"error"}:
                return {"granted": False, "error": "unexpected coordinator response"}
        else:
            return {"granted": False, "error": "invalid coordinator response"}
        return result
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


def _independent_client(port, owner, barrier, now=0):
    import os
    barrier.wait(timeout=10)
    result = request(port, {"op": "grant", "owner": owner, "now": now, "ttl": 5})
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


def test_tcp_lease_does_not_authorize_other_owner_after_malformed_request(tmp_path):
    """A truncated JSON request cannot grant admission or mutate active lease."""
    db = str(tmp_path / "truncated-json.sqlite")
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
            # Send an incomplete request over a disposable local TCP socket.
            with socket.create_connection(("127.0.0.1", port), timeout=1.5) as conn:
                conn.settimeout(1.5)
                conn.sendall(b'{"op": "grant", "owner": "intruder",')
                conn.shutdown(socket.SHUT_WR)
                try:
                    response = conn.recv(4096)
                except (OSError, ConnectionError):
                    response = b""
            assert b'"granted": true' not in response.lower()
            with _connect(db) as con:
                assert con.execute(
                    "SELECT owner, generation, deadline FROM active_lease WHERE id=1"
                ).fetchone() == ("first", 1, 5)
            assert request(port, {
                "op": "grant", "owner": "second", "now": 1, "ttl": 5
            })["granted"] is False
        finally:
            server.shutdown()
            thread.join(timeout=5)


def test_tcp_coordinator_restart_preserves_fence_after_lost_grant_ack(tmp_path):
    """Unknown grant outcome remains fail-closed across coordinator restart."""
    db = str(tmp_path / "lost-grant-restart.sqlite")
    with _connect(db) as con:
        con.execute(
            "CREATE TABLE active_lease(id INTEGER PRIMARY KEY, "
            "owner TEXT NOT NULL, generation INTEGER NOT NULL, "
            "deadline REAL NOT NULL)"
        )
    with AdmissionServer(("127.0.0.1", 0), AdmissionHandler) as first:
        first.db = db
        port = first.server_address[1]
        worker = threading.Thread(target=first.serve_forever, daemon=True)
        worker.start()
        try:
            assert request(port, {
                "op": "grant_disconnect", "owner": "worker-a", "now": 0, "ttl": 5
            })["granted"] is False
        finally:
            first.shutdown()
            worker.join(timeout=5)

    # The lease persists even though its grant acknowledgement was lost.
    with _connect(db) as con:
        assert con.execute(
            "SELECT owner, generation, deadline FROM active_lease WHERE id=1"
        ).fetchone() == ("worker-a", 1, 5)

    with AdmissionServer(("127.0.0.1", 0), AdmissionHandler) as recovered:
        recovered.db = db
        port = recovered.server_address[1]
        worker = threading.Thread(target=recovered.serve_forever, daemon=True)
        worker.start()
        try:
            assert request(port, {
                "op": "grant", "owner": "worker-a", "now": 1, "ttl": 5
            })["granted"] is False
            assert request(port, {
                "op": "grant", "owner": "worker-b", "now": 4, "ttl": 5
            })["granted"] is False
            assert request(port, {
                "op": "grant", "owner": "worker-b", "now": 5, "ttl": 5
            }) == {"granted": True, "generation": 2}
            assert request(port, {
                "op": "release", "owner": "worker-a", "generation": 1
            }) == {"released": False}
            with _connect(db) as con:
                assert con.execute(
                    "SELECT owner, generation, deadline FROM active_lease WHERE id=1"
                ).fetchone() == ("worker-b", 2, 10)
        finally:
            recovered.shutdown()
            worker.join(timeout=5)


def test_tcp_restart_after_lost_grant_ack_keeps_k1_for_competing_clients(tmp_path):
    """At lease expiry after lost ACK + restart, only one TCP client wins."""
    from concurrent.futures import ThreadPoolExecutor

    db = str(tmp_path / "lost-grant-race.sqlite")
    with _connect(db) as con:
        con.execute(
            "CREATE TABLE active_lease(id INTEGER PRIMARY KEY, "
            "owner TEXT NOT NULL, generation INTEGER NOT NULL, "
            "deadline REAL NOT NULL)"
        )
    with AdmissionServer(("127.0.0.1", 0), AdmissionHandler) as first:
        first.db = db
        port = first.server_address[1]
        worker = threading.Thread(target=first.serve_forever, daemon=True)
        worker.start()
        try:
            assert request(port, {
                "op": "grant_disconnect", "owner": "original", "now": 0, "ttl": 5
            })["granted"] is False
        finally:
            first.shutdown()
            worker.join(timeout=5)

    with AdmissionServer(("127.0.0.1", 0), AdmissionHandler) as recovered:
        recovered.db = db
        port = recovered.server_address[1]
        worker = threading.Thread(target=recovered.serve_forever, daemon=True)
        worker.start()
        try:
            gate = threading.Barrier(2)

            def contend(owner):
                gate.wait(timeout=5)
                return owner, request(port, {
                    "op": "grant", "owner": owner, "now": 5, "ttl": 5
                })

            with ThreadPoolExecutor(max_workers=2) as pool:
                futures = [pool.submit(contend, owner) for owner in ("a", "b")]
                results = [future.result(timeout=10) for future in futures]
            winners = [(owner, result) for owner, result in results if result["granted"]]
            assert len(winners) == 1
            assert winners[0][1] == {"granted": True, "generation": 2}
            assert request(port, {
                "op": "release", "owner": "original", "generation": 1
            }) == {"released": False}
            with _connect(db) as con:
                assert con.execute(
                    "SELECT owner, generation, deadline FROM active_lease WHERE id=1"
                ).fetchone() == (winners[0][0], 2, 10)
        finally:
            recovered.shutdown()
            worker.join(timeout=5)


def test_spawned_clients_compete_at_expiry_after_lost_ack_restart(tmp_path):
    """Distinct client PIDs compete for K=1 after a lost ACK and TCP restart.

    All processes remain on one CI host; this is NOT independent-host proof.
    """
    import multiprocessing
    from concurrent.futures import ProcessPoolExecutor

    db = str(tmp_path / "spawned-lost-ack-restart.sqlite")
    with _connect(db) as con:
        con.execute(
            "CREATE TABLE active_lease(id INTEGER PRIMARY KEY, "
            "owner TEXT NOT NULL, generation INTEGER NOT NULL, "
            "deadline REAL NOT NULL)"
        )
    with AdmissionServer(("127.0.0.1", 0), AdmissionHandler) as first:
        first.db = db
        port = first.server_address[1]
        server_thread = threading.Thread(target=first.serve_forever, daemon=True)
        server_thread.start()
        try:
            assert request(port, {
                "op": "grant_disconnect", "owner": "original", "now": 0, "ttl": 5
            })["granted"] is False
        finally:
            first.shutdown()
            server_thread.join(timeout=5)

    ctx = multiprocessing.get_context("spawn")
    with AdmissionServer(("127.0.0.1", 0), AdmissionHandler) as recovered:
        recovered.db = db
        port = recovered.server_address[1]
        server_thread = threading.Thread(target=recovered.serve_forever, daemon=True)
        server_thread.start()
        try:
            # After a lost ACK, even another client process must fail closed
            # before the original persisted lease expires.
            with ctx.Pool(processes=1) as isolated:
                prior = isolated.apply(request, (port, {
                    "op": "grant", "owner": "early-client", "now": 4, "ttl": 5
                }))
            assert prior["granted"] is False
            with _connect(db) as con:
                assert con.execute(
                    "SELECT owner, generation, deadline FROM active_lease WHERE id=1"
                ).fetchone() == ("original", 1, 5)

            with ctx.Manager() as manager:
                barrier = manager.Barrier(2)
                with ProcessPoolExecutor(max_workers=2, mp_context=ctx) as pool:
                    futures = [
                        pool.submit(_independent_client, port, owner, barrier, 5)
                        for owner in ("client-a", "client-b")
                    ]
                    results = [future.result(timeout=20) for future in futures]
            assert len({pid for pid, _, _ in results}) == 2
            winners = [(owner, result) for _, owner, result in results if result["granted"]]
            assert len(winners) == 1
            assert winners[0][1] == {"granted": True, "generation": 2}
            # Exercise the stale release from a different process, not the
            # parent test runner that issued the initial grant.
            with ctx.Pool(processes=1) as isolated:
                stale_release = isolated.apply(request, (port, {
                    "op": "release", "owner": "original", "generation": 1
                }))
            assert stale_release == {"released": False}
            assert request(port, {
                "op": "grant", "owner": "intruder", "now": 6, "ttl": 5
            })["granted"] is False
            with _connect(db) as con:
                assert con.execute(
                    "SELECT owner, generation, deadline FROM active_lease WHERE id=1"
                ).fetchone() == (winners[0][0], 2, 10)
        finally:
            recovered.shutdown()
            server_thread.join(timeout=5)


def test_tcp_untrusted_grant_reply_requires_positive_integer_generation():
    """Test-only client refuses malformed grant responses over actual loopback TCP."""
    class ReplyHandler(socketserver.StreamRequestHandler):
        def handle(self):
            self.rfile.readline()
            self.wfile.write((json.dumps(self.server.reply) + "\n").encode("utf-8"))

    with AdmissionServer(("127.0.0.1", 0), ReplyHandler) as server:
        port = server.server_address[1]
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            for reply in (
                True, [], "approved", {"granted": True},
                {"granted": True, "generation": 0},
                {"granted": True, "generation": -1},
                {"granted": True, "generation": True},
                {"granted": True, "generation": "7"},
                {"granted": "true", "generation": 7},
                {"granted": True, "generation": 7, "error": "unexpected"},
                {"granted": True, "generation": 7, "released": True},
            ):
                server.reply = reply
                received = request(port, {"op": "grant", "owner": "test"})
                assert received["granted"] is False, (reply, received)
            for rejected in (
                {"granted": False},
                {"granted": False, "generation": 1},
                {"granted": False, "generation": None, "released": True},
                {"granted": False, "generation": None, "error": "extra"},
            ):
                server.reply = rejected
                denied = request(port, {"op": "grant", "owner": "test"})
                assert denied["granted"] is False
                assert denied.get("error") == "unexpected coordinator response"
            server.reply = {"granted": False, "generation": None}
            assert request(port, {"op": "grant", "owner": "test"}) == server.reply
            server.reply = {"granted": True, "generation": 7}
            assert request(port, {"op": "grant", "owner": "test"}) == server.reply
            assert request(port, {"op": "release", "owner": "test", "generation": 7})["granted"] is False
            server.reply = {"released": True}
            assert request(port, {"op": "grant", "owner": "test"})["granted"] is False
            assert request(port, {"op": "release", "owner": "test", "generation": 7}) == {"released": True}
            server.reply = {"released": True, "granted": True, "generation": 7}
            assert request(port, {"op": "release", "owner": "test", "generation": 7})["granted"] is False
        finally:
            server.shutdown()
            thread.join(timeout=5)


def test_server_clock_and_authenticated_owner_reject_client_time_spoofing(tmp_path):
    """Isolated security prototype: server owns time, TTL policy and owner mapping.

    This is a test-only loopback characterization, not production TLS/mTLS.
    """
    db = str(tmp_path / "server-clock-security.sqlite")
    with _connect(db) as con:
        con.execute(
            "CREATE TABLE active_lease(id INTEGER PRIMARY KEY, "
            "owner TEXT NOT NULL, generation INTEGER NOT NULL, "
            "deadline REAL NOT NULL)"
        )

    class ControlledHandler(socketserver.StreamRequestHandler):
        def handle(self):
            payload = json.loads(self.rfile.readline().decode("utf-8"))
            credential = payload.get("credential")
            identity = (
                self.server.identities.get(credential)
                if type(credential) is str else None
            )
            if identity is None:
                response = {"error": "unauthorized"}
            elif payload.get("op") == "grant":
                # Never honor caller-controlled 'now', 'ttl' or 'owner'.
                generation = _grant(
                    self.server.db, identity, self.server.clock["now"],
                    self.server.fixed_ttl,
                )
                response = {"granted": generation is not None, "generation": generation}
            elif payload.get("op") == "release":
                generation = payload.get("generation")
                if type(generation) is not int or generation < 1:
                    response = {"released": False}
                else:
                    response = {"released": _release(self.server.db, identity, generation)}
            else:
                response = {"error": "unsupported operation"}
            self.wfile.write((json.dumps(response) + "\n").encode("utf-8"))

    with AdmissionServer(("127.0.0.1", 0), ControlledHandler) as server:
        server.db = db
        server.clock = {"now": 100}
        server.fixed_ttl = 10
        server.identities = {"credential-a": "identity-a", "credential-b": "identity-b"}
        port = server.server_address[1]
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            assert request(port, {
                "op": "grant", "credential": "credential-a",
                "owner": "identity-b", "now": 10**9, "ttl": 10**9
            }) == {"granted": True, "generation": 1}
            with _connect(db) as con:
                assert con.execute(
                    "SELECT owner, generation, deadline FROM active_lease WHERE id=1"
                ).fetchone() == ("identity-a", 1, 110)

            # Time spoofing, unbounded TTL, and impersonation cannot bypass K=1.
            assert request(port, {
                "op": "grant", "credential": "credential-b",
                "owner": "identity-a", "now": 10**12, "ttl": 0
            }) == {"granted": False, "generation": None}
            assert request(port, {
                "op": "release", "credential": "credential-b",
                "owner": "identity-a", "generation": 1
            }) == {"released": False}
            assert request(port, {
                "op": "grant", "credential": "invalid",
                "now": 10**12, "ttl": 10**12
            }) == {"error": "unauthorized"}
            for invalid_credential in (None, 42, True, [], {}, ["credential-a"]):
                denied = request(port, {
                    "op": "grant", "credential": invalid_credential,
                    "now": 10**12, "ttl": 10**12
                })
                assert denied == {"error": "unauthorized"}
            with _connect(db) as con:
                assert con.execute(
                    "SELECT owner, generation, deadline FROM active_lease WHERE id=1"
                ).fetchone() == ("identity-a", 1, 110)

            server.clock["now"] = 110
            assert request(port, {
                "op": "grant", "credential": "credential-b", "now": 0, "ttl": 10**9
            }) == {"granted": True, "generation": 2}
            assert request(port, {
                "op": "release", "credential": "credential-a", "generation": 1
            }) == {"released": False}
            with _connect(db) as con:
                assert con.execute(
                    "SELECT owner, generation, deadline FROM active_lease WHERE id=1"
                ).fetchone() == ("identity-b", 2, 120)
        finally:
            server.shutdown()
            thread.join(timeout=5)
