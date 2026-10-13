"""SG28 disposable staging readiness probe, not a DIST-01 acceptance test.

Uses existing authenticated transport and fails closed. It never acquires
capacity, modifies leases, runs calculations, or logs credentials.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from app.services.distributed_admission import DistributedAdmissionUnavailable
from app.services.distributed_tls_transport import CoordinatorTLSConfig


def assess(config: CoordinatorTLSConfig, *, explicitly_disposable: bool) -> dict:
    """Static configuration validation only; no network connection is opened."""
    if not explicitly_disposable:
        raise DistributedAdmissionUnavailable("Disposable staging authorization required")
    config.validate()
    if config.host in ("localhost", "127.0.0.1", "::1"):
        raise DistributedAdmissionUnavailable("Independent-host probe needs a non-loopback coordinator")
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
