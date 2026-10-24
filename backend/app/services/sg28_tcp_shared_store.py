"""SG28 experimental TCP lease client. Not wired to /evaluate or production.

Protocol: one JSON line request/reply per connection. A missing/malformed ACK
never authorizes execution. TLS/authentication and independent-host validation
are REQUIRED before any non-disposable deployment.
"""
import json
import socket

from app.services.shared_admission_contract import SharedLease


def _unique_fields(pairs):
    """Reject ambiguous coordinator acknowledgements at every JSON object level."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate coordinator response field")
        result[key] = value
    return result


class TcpSharedLeaseStore:
    """Transport-only store for an explicitly configured disposable coordinator."""

    def __init__(self, host: str, port: int, timeout: float = 1.0):
        if not host or not (1 <= port <= 65535) or not (0 < timeout <= 5):
            raise ValueError("invalid bounded coordinator address or timeout")
        self.host, self.port, self.timeout = host, port, timeout

    def _exchange(self, payload: dict) -> dict:
        data = (json.dumps(payload, allow_nan=False) + "\n").encode("utf-8")
        with socket.create_connection((self.host, self.port), timeout=self.timeout) as sock:
            sock.settimeout(self.timeout)
            sock.sendall(data)
            with sock.makefile("rb") as reader:
                line = reader.readline(8193)
        if not line or len(line) > 8192 or not line.endswith(b"\n"):
            raise ConnectionError("coordinator reply missing or too large")
        reply = json.loads(line.decode("utf-8"), object_pairs_hook=_unique_fields,
                           parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite coordinator value")))
        if not isinstance(reply, dict):
            raise ValueError("coordinator reply must be an object")
        return reply

    def acquire(self, owner: str, ttl: float) -> SharedLease | None:
        response = self._exchange({"op": "grant", "owner": owner, "ttl": ttl})
        if response.get("granted") is False:
            if response.get("error"):
                raise ConnectionError("coordinator rejected with an error")
            return None
        if response.get("granted") is not True:
            raise ValueError("unconfirmed lease grant")
        if "error" in response:
            raise ValueError("contradictory coordinator grant acknowledgement")
        return SharedLease(response.get("owner"), response.get("generation"), response.get("deadline"))

    def release(self, lease: SharedLease) -> bool:
        response = self._exchange({"op": "release", "owner": lease.owner, "generation": lease.generation})
        if type(response.get("released")) is not bool:
            raise ValueError("unconfirmed lease release")
        if "error" in response:
            raise ValueError("contradictory coordinator release acknowledgement")
        return response["released"]
