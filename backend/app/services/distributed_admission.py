"""SG28 distributed admission contract (not yet wired into public routes).

This module deliberately provides no network implementation: callers must supply
an authenticated transport and a server-side coordinator with durable fencing.
Importing it has no side effects. The distributed mode stays disabled by default.
"""
from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Callable, Mapping, Any


class DistributedAdmissionUnavailable(RuntimeError):
    """No trustworthy authorization was received from a shared coordinator."""


@dataclass(frozen=True)
class AdmissionGrant:
    generation: int


def distributed_admission_enabled() -> bool:
    """Explicit opt-in only; absence of a coordinator never enables execution."""
    return os.getenv("SG28_DISTRIBUTED_ADMISSION", "0") == "1"


def validate_grant(reply: Any) -> AdmissionGrant:
    """Accept only an unambiguous, strictly typed server response."""
    if (
        type(reply) is not dict
        or set(reply) != {"granted", "generation"}
        or reply["granted"] is not True
        or type(reply["generation"]) is not int
        or reply["generation"] < 1
    ):
        raise DistributedAdmissionUnavailable("Shared admission denied or unverifiable")
    return AdmissionGrant(generation=reply["generation"])


def acquire_distributed_admission(
    authenticated_exchange: Callable[[Mapping[str, str]], Any] | None,
) -> AdmissionGrant:
    """Fail closed until an explicitly enabled authenticated exchange exists.

    The authenticated exchange must derive identity from secure transport; never
    accept caller-supplied owner, clock or TTL as authorization. The lifetime
    and release of the returned generation remain the integration caller's duty.
    """
    if not distributed_admission_enabled() or authenticated_exchange is None:
        raise DistributedAdmissionUnavailable("Distributed admission not configured")
    try:
        reply = authenticated_exchange({"op": "grant"})
    except Exception as exc:
        raise DistributedAdmissionUnavailable("Shared coordinator unreachable") from exc
    return validate_grant(reply)
