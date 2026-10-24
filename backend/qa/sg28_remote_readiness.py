"""SG28 disposable staging readiness probe, not a DIST-01 acceptance test.

Uses existing authenticated transport and fails closed. It never acquires
capacity, modifies leases, runs calculations, or logs credentials.
"""
from __future__ import annotations

import argparse
import ipaddress
import json
import os
import socket
import sys

from app.services.distributed_admission import DistributedAdmissionUnavailable
from app.services.distributed_tls_transport import CoordinatorTLSConfig


def _is_local_or_unroutable(value: str) -> bool:
    """Reject local endpoints, including alternate loopback IP spellings."""
    name = value.strip().rstrip(".").lower()
    if name == "localhost" or name.endswith(".localhost"):
        return True
    try:
        address = ipaddress.ip_address(name.strip("[]"))
    except ValueError:
        # inet_aton recognizes legacy short and integer IPv4 forms such as
        # 127.1 or 2130706433; reject their local equivalents without DNS.
        try:
            address = ipaddress.IPv4Address(socket.inet_aton(name))
        except (OSError, ValueError):
            return False
    if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped:
        address = address.ipv4_mapped
    return (address.is_loopback or address.is_unspecified
            or address.is_link_local or address.is_multicast)


def assess(config: CoordinatorTLSConfig, *, explicitly_disposable: bool) -> dict:
    """Static configuration validation only; no network connection is opened."""
    if not explicitly_disposable:
        raise DistributedAdmissionUnavailable("Disposable staging authorization required")
    config.validate()
    if _is_local_or_unroutable(config.host):
        raise DistributedAdmissionUnavailable("Independent-host probe needs a non-loopback coordinator")
    if _is_local_or_unroutable(config.server_name):
        raise DistributedAdmissionUnavailable("Remote coordinator requires a non-loopback TLS identity")
    return {
        "ready_for_connectivity_probe": True,
        "tls_identity_check_configured": True,
        "authorization": "disposable_staging_only",
        "network_test_executed": False,
        "dist01_certified": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate SG28 disposable remote test inputs")
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--server-name", required=True)
    parser.add_argument("--ca", required=True)
    parser.add_argument("--client-cert", required=True)
    parser.add_argument("--client-key", required=True)
    args = parser.parse_args()
    try:
        result = assess(
            CoordinatorTLSConfig(
                args.host, args.port, args.server_name,
                args.ca, args.client_cert, args.client_key,
            ),
            explicitly_disposable=os.environ.get("SG28_DISPOSABLE_STAGING_AUTHORIZED") == "1",
        )
    except (DistributedAdmissionUnavailable, ValueError, OSError):
        print(json.dumps({"ready_for_connectivity_probe": False,
                          "network_test_executed": False,
                          "dist01_certified": False}))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
