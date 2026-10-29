"""EN-SG-32: opt-in, in-process rate limiting (single host).

Design constraints recorded for the certification audit:

- **Disabled by default.** ``RATE_LIMIT_REQUESTS=0`` (the shipped default) means
  the middleware never throttles and never adds ``X-RateLimit-*`` headers, so a
  deployment that has not opted in keeps the exact previous behaviour.
- **Fixed window per client key.** A window of ``RATE_LIMIT_WINDOW_SECONDS``
  (default 60) admits ``RATE_LIMIT_REQUESTS`` calls; the next call in the same
  window is rejected with ``429`` and ``Retry-After``.
- **No distributed state.** The counter lives in this process. Multi-host or
  multi-worker correctness would need a shared store, which the single-host H2
  certification scope does not include (``H2-SG28-DIST-01..08`` remains
  ``OUT_OF_SCOPE_SINGLE_HOST``).
- **Client identity.** The peer address by default. ``X-Forwarded-For`` is
  ignored unless ``RATE_LIMIT_TRUST_FORWARDED_FOR=true``, because an untrusted
  client can forge that header to obtain a fresh bucket per request.
- **Bounded memory.** At most ``RATE_LIMIT_MAX_TRACKED_CLIENTS`` buckets are
  kept; the least recently seen is evicted first. An evicted client starts a
  new window, which is the safe direction for this control (a client cannot
  force eviction cheaply enough to gain unlimited throughput in practice) and
  is asserted by the regression suite.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, Dict, Optional, Tuple

from app.core.config import API_V1_PREFIX

# Paths that must stay reachable even when the caller is being throttled:
# liveness probes and the schema/docs endpoints used by tooling. Matched
# exactly, so user traffic cannot inherit an exemption by ending in "/docs".
EXEMPT_PATHS = frozenset(
    {
        f"{API_V1_PREFIX}/health",
        f"{API_V1_PREFIX}/docs",
        f"{API_V1_PREFIX}/docs/oauth2-redirect",
        f"{API_V1_PREFIX}/redoc",
        f"{API_V1_PREFIX}/openapi.json",
    }
)


def is_exempt_path(path: str) -> bool:
    """Return True only for the exact liveness/documentation endpoints."""
    return path in EXEMPT_PATHS


def client_key(request, trust_forwarded_for: bool) -> str:
    """Derive the bucket key for a request.

    ``X-Forwarded-For`` keeps the left-most entry (the originating client), as
    written by well-behaved proxies. Values are only trusted when the operator
    opted in through ``RATE_LIMIT_TRUST_FORWARDED_FOR``.
    """
    if trust_forwarded_for:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            first = forwarded.split(",")[0].strip()
            if first:
                return first
    client = getattr(request, "client", None)
    host = getattr(client, "host", None)
    return host or "unknown"


@dataclass(frozen=True)
class RateLimitDecision:
    allowed: bool
    limit: int
    remaining: int
    reset_after: float
    retry_after: float


class FixedWindowRateLimiter:
    """Fixed-window counter with an injectable monotonic clock."""

    def __init__(
        self,
        requests: int,
        window_seconds: float,
        trust_forwarded_for: bool = False,
        clock: Optional[Callable[[], float]] = None,
        max_tracked_clients: int = 10_000,
    ) -> None:
        if requests < 0:
            raise ValueError("RATE_LIMIT_REQUESTS must be >= 0 (0 disables it)")
        if window_seconds <= 0:
            raise ValueError("RATE_LIMIT_WINDOW_SECONDS must be > 0")
        if max_tracked_clients < 1:
            raise ValueError("max_tracked_clients must be >= 1")
        self.requests = requests
        self.window_seconds = float(window_seconds)
        self.trust_forwarded_for = trust_forwarded_for
        self.max_tracked_clients = max_tracked_clients
        self._clock = clock or time.monotonic
        # key -> (window_start, used, last_seen)
        self._buckets: Dict[str, Tuple[float, int, float]] = {}

    @property
    def enabled(self) -> bool:
        return self.requests > 0

    @property
    def tracked_clients(self) -> int:
        return len(self._buckets)

    def check(self, key: str) -> RateLimitDecision:
        if not self.enabled:
            return RateLimitDecision(True, 0, 0, 0.0, 0.0)

        now = self._clock()
        window_start, used, _ = self._buckets.get(key, (now, 0, now))
        if now - window_start >= self.window_seconds:
            window_start, used = now, 0

        if used >= self.requests:
            reset_after = max(self.window_seconds - (now - window_start), 0.0)
            self._buckets[key] = (window_start, used, now)
            return RateLimitDecision(
                allowed=False,
                limit=self.requests,
                remaining=0,
                reset_after=reset_after,
                retry_after=reset_after,
            )

        used += 1
        self._buckets[key] = (window_start, used, now)
        self._evict_if_needed()
        reset_after = max(self.window_seconds - (now - window_start), 0.0)
        return RateLimitDecision(
            allowed=True,
            limit=self.requests,
            remaining=self.requests - used,
            reset_after=reset_after,
            retry_after=0.0,
        )

    def _evict_if_needed(self) -> None:
        overflow = len(self._buckets) - self.max_tracked_clients
        if overflow <= 0:
            return
        oldest = sorted(self._buckets.items(), key=lambda item: item[1][2])[:overflow]
        for key, _ in oldest:
            self._buckets.pop(key, None)
