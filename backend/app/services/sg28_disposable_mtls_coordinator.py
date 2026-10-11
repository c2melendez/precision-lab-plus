"""SG28 disposable mTLS lease coordinator, never imported by public routes.

For isolated integration tests only: loopback TCP, ephemeral certificates, SQLite
on one host. Do not expose this handler publicly or call it distributed proof.
"""
from __future__ import annotations

import json
import socketserver
import ssl
import time

from app.services.sg28_sqlite_lease_store import SQLiteLeaseStore


class _LeaseHandler(socketserver.StreamRequestHandler):
    def handle(self):
        peer = self.request.getpeercert()
        if not peer:
            return
        names = [
            value for rdn in peer.get("subject", ())
            for key, value in rdn if key == "commonName"
        ]
        if len(names) != 1 or names[0] not in self.server.allowed_identities:
            self.wfile.write(b'{"error":"unauthorized"}\n')
            return
        identity = names[0]
        line = self.rfile.readline(4097)
        if not line.endswith(b"\n") or len(line) > 4096:
            return
        try:
            request = json.loads(line)
        except (ValueError, UnicodeError):
            return
        if type(request) is not dict:
            return
        if request == {"op": "grant"}:
            lease = self.server.store.acquire(identity, now=self.server.clock())
            reply = (
                {"granted": True, "generation": lease.generation}
                if lease else {"granted": False, "generation": None}
            )
        elif (
            set(request) == {"op", "generation"}
            and request.get("op") == "release"
            and type(request.get("generation")) is int
            and request["generation"] >= 1
        ):
            reply = {
                "released": self.server.store.release(identity, request["generation"])
            }
        else:
            reply = {"error": "unsupported operation"}
        self.wfile.write((json.dumps(reply) + "\n").encode())


class DisposableMTLSLeaseServer(socketserver.ThreadingTCPServer):
    """Test-only TLS service; cert chains and identities must be supplied."""

    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, address, *, ssl_context: ssl.SSLContext,
                 store: SQLiteLeaseStore, allowed_identities: set[str],
                 clock=time.time):
        if address[0] not in ("127.0.0.1", "localhost", "::1"):
            raise ValueError("Disposable SG28 server must stay on loopback")
        if ssl_context.verify_mode != ssl.CERT_REQUIRED:
            raise ValueError("Disposable SG28 server requires client certificates")
        self.tls_context = ssl_context
        self.store = store
        self.allowed_identities = frozenset(allowed_identities)
        self.clock = clock
        super().__init__(address, _LeaseHandler)

    def get_request(self):
        plain, address = super().get_request()
        try:
            plain.settimeout(3)
            return self.tls_context.wrap_socket(plain, server_side=True), address
        except BaseException:
            plain.close()
            raise
