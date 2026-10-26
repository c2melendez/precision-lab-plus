"""SG28 experimental authenticated TLS transport; not connected to /evaluate.

The caller supplies explicitly provisioned certificate paths and trusted DNS name.
No fallback to plaintext, no implicit trust, no persistent connections.
"""
from __future__ import annotations

import json
import math
import socket
import ssl
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from app.services.distributed_admission import DistributedAdmissionUnavailable


@dataclass(frozen=True)
class CoordinatorTLSConfig:
    host: str
    port: int
    server_name: str
    ca_file: str
    client_cert_file: str
    client_key_file: str
    timeout_seconds: float = 2.0

    def validate(self) -> None:
        if (not isinstance(self.host, str) or not self.host.strip()
                or not isinstance(self.server_name, str) or not self.server_name.strip()
                or type(self.port) is not int or not 1 <= self.port <= 65535):
            raise DistributedAdmissionUnavailable("Invalid coordinator address")
        if (type(self.timeout_seconds) not in (float, int)
                or not math.isfinite(self.timeout_seconds)
                or not 0 < self.timeout_seconds <= 10):
            raise DistributedAdmissionUnavailable("Invalid coordinator timeout")
        if not all(isinstance(path, str) and path and Path(path).is_file()
                   for path in (self.ca_file, self.client_cert_file, self.client_key_file)):
            raise DistributedAdmissionUnavailable("Coordinator trust material missing")


def make_mtls_exchange(config: CoordinatorTLSConfig):
    """Return a strictly authenticated, one-request-per-TLS-connection exchange."""
    config.validate()
    context = ssl.create_default_context(
        purpose=ssl.Purpose.SERVER_AUTH, cafile=config.ca_file
    )
    context.verify_mode = ssl.CERT_REQUIRED
    context.check_hostname = True
    context.load_cert_chain(config.client_cert_file, config.client_key_file)

    def exchange(payload: Mapping[str, Any]) -> Any:
        if type(payload) is not dict or set(payload) not in (
            {"op"}, {"op", "generation"}
        ) or payload.get("op") not in ("grant", "release"):
            raise DistributedAdmissionUnavailable("Invalid coordinator request")
        if payload["op"] == "grant" and set(payload) != {"op"}:
            raise DistributedAdmissionUnavailable("Invalid grant request")
        if payload["op"] == "release" and (
            set(payload) != {"op", "generation"}
            or type(payload["generation"]) is not int or payload["generation"] < 1
        ):
            raise DistributedAdmissionUnavailable("Invalid release request")
        message = (json.dumps(payload, separators=(",", ":")) + "\n").encode()
        try:
            with socket.create_connection(
                (config.host, config.port), timeout=config.timeout_seconds
            ) as plain:
                with context.wrap_socket(
                    plain, server_hostname=config.server_name
                ) as secure:
                    secure.settimeout(config.timeout_seconds)
                    secure.sendall(message)
                    data = bytearray()
                    while len(data) <= 4096:
                        block = secure.recv(4097 - len(data))
                        if not block:
                            break
                        data.extend(block)
                        if b"\n" in block:
                            break
            if len(data) > 4096 or not data.endswith(b"\n") or data.count(b"\n") != 1:
                raise DistributedAdmissionUnavailable("Invalid coordinator frame")
            return json.loads(data)
        except (OSError, ssl.SSLError, ValueError, UnicodeError) as exc:
            raise DistributedAdmissionUnavailable("Authenticated coordinator unavailable") from exc

    return exchange
