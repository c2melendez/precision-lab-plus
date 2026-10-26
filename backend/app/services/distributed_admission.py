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
    authenticated_exchange: Callable[[Mapping[str, Any]], Any] | None,
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


def release_distributed_admission(
    authenticated_exchange: Callable[[Mapping[str, Any]], Any] | None,
    grant: AdmissionGrant,
) -> None:
    """Require a confirmed fenced release, never infer one from a lost reply."""
    if not distributed_admission_enabled() or authenticated_exchange is None:
        raise DistributedAdmissionUnavailable("Distributed release not configured")
    if type(grant) is not AdmissionGrant or type(grant.generation) is not int or grant.generation < 1:
        raise DistributedAdmissionUnavailable("Invalid lease generation")
    try:
        reply = authenticated_exchange({"op": "release", "generation": grant.generation})
    except Exception as exc:
        raise DistributedAdmissionUnavailable("Shared coordinator release unconfirmed") from exc
    if type(reply) is not dict or set(reply) != {"released"} or reply["released"] is not True:
        raise DistributedAdmissionUnavailable("Shared coordinator release unconfirmed")


from contextlib import contextmanager


@contextmanager
def distributed_admission_lease(
    authenticated_exchange: Callable[[Mapping[str, Any]], Any] | None,
):
    """Reserve for a complete logical task; release after the caller exits.

    If release is unconfirmed, fail closed and preserve fencing server-side.
    Callers must finish child workers before leaving this context.
    """
    grant = acquire_distributed_admission(authenticated_exchange)
    try:
        yield grant
    finally:
        release_distributed_admission(authenticated_exchange, grant)
