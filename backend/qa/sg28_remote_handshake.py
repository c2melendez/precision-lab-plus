"""SG28 remote handshake-only probe for authorized disposable staging.

No admission protocol payload is ever transmitted; not DIST certification.
"""
from __future__ import annotations
import argparse
import json
import os
import socket
import ssl
import sys
from app.services.distributed_admission import DistributedAdmissionUnavailable
from app.services.distributed_tls_transport import CoordinatorTLSConfig
from qa.sg28_remote_readiness import assess

def probe(config: CoordinatorTLSConfig, *, explicitly_disposable: bool) -> dict:
    assess(config, explicitly_disposable=explicitly_disposable)
    try:
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=config.ca_file)
        context.verify_mode = ssl.CERT_REQUIRED
        context.check_hostname = True
        context.load_cert_chain(config.client_cert_file, config.client_key_file)
        with socket.create_connection((config.host, config.port), timeout=config.timeout_seconds) as plain:
            with context.wrap_socket(plain, server_hostname=config.server_name) as secure:
                secure.settimeout(config.timeout_seconds)
                if not secure.getpeercert():
                    raise DistributedAdmissionUnavailable("Remote peer identity unavailable")
    except (OSError, ssl.SSLError, ValueError) as exc:
        raise DistributedAdmissionUnavailable("Remote mTLS handshake failed") from exc
    return {"mtls_handshake_verified": True, "admission_request_sent": False,
            "dist01_certified": False, "dist08_certified": False}

def main() -> int:
    parser = argparse.ArgumentParser(description="SG28 remote handshake-only preflight")
    for arg in ("host", "server-name", "ca", "client-cert", "client-key"):
        parser.add_argument("--" + arg, required=True)
    parser.add_argument("--port", required=True, type=int)
    args = parser.parse_args()
    config = CoordinatorTLSConfig(args.host, args.port, args.server_name,
                                  args.ca, args.client_cert, args.client_key)
    try:
        result = probe(config, explicitly_disposable=os.getenv("SG28_DISPOSABLE_STAGING_AUTHORIZED") == "1")
    except (DistributedAdmissionUnavailable, ValueError, OSError):
        print(json.dumps({"mtls_handshake_verified": False, "admission_request_sent": False,
                          "dist01_certified": False, "dist08_certified": False}))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0

if __name__ == "__main__":
    sys.exit(main())
