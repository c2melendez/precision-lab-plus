"""EN-SG-32: opt-in rate limiting (in-process TestClient only).

The limiter is disabled by default (RATE_LIMIT_REQUESTS=0), so these tests
inject an explicitly enabled limiter through ``app.state.rate_limiter`` and
drive its clock, instead of sleeping. No request leaves the process.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.rate_limit import FixedWindowRateLimiter


class FakeClock:
    def __init__(self) -> None:
        self.now = 1_000.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


@pytest.fixture
def restore_limiter():
    original = getattr(app.state, "rate_limiter", None)
    yield
    app.state.rate_limiter = original


def _client(client_host=("testclient", 50000)) -> TestClient:
    return TestClient(app, raise_server_exceptions=False, client=client_host)


def _enable(requests: int, window: float = 60.0, trust_forwarded_for: bool = False):
    clock = FakeClock()
    limiter = FixedWindowRateLimiter(
        requests=requests,
        window_seconds=window,
        trust_forwarded_for=trust_forwarded_for,
        clock=clock,
    )
    app.state.rate_limiter = limiter
    return limiter, clock


def _evaluate(client: TestClient, headers=None):
    return client.post(
        "/api/v1/evaluate",
        json={"expression": "1+1", "angle_unit": "rad"},
        headers=headers or {},
    )


def test_in625_h2_sg32_default_is_disabled_no_rate_limit_headers(restore_limiter):
    """Shipped default must not throttle: 20 rapid calls, no 429, no headers."""
    limiter = FixedWindowRateLimiter(requests=0, window_seconds=60.0)
    app.state.rate_limiter = limiter
    assert limiter.enabled is False

    client = _client()
    for _ in range(20):
        response = _evaluate(client)
        assert response.status_code == 200, response.text[:180]
        assert "X-RateLimit-Limit" not in response.headers
        assert response.headers.get("Retry-After") is None


def test_in625_h2_sg32_burst_over_limit_returns_429_with_retry_after(restore_limiter):
    """EN-SG-32 burst: the (N+1)th call in the window is rejected, bounded time."""
    import time

    _enable(requests=3)

    client = _client()
    started = time.perf_counter()
    allowed = [_evaluate(client) for _ in range(3)]
    rejected = _evaluate(client)
    elapsed = time.perf_counter() - started

    assert [r.status_code for r in allowed] == [200, 200, 200]
    assert [r.headers["X-RateLimit-Remaining"] for r in allowed] == ["2", "1", "0"]
    assert rejected.status_code == 429
    assert elapsed < 2.0

    body = rejected.json()
    assert body["success"] is False
    assert body["error_code"] == "RATE_LIMITED"
    assert body["request_id"]
    assert rejected.headers["X-Request-ID"] == body["request_id"]
    assert rejected.headers["X-RateLimit-Limit"] == "3"
    assert rejected.headers["X-RateLimit-Remaining"] == "0"
    retry_after = float(rejected.headers["Retry-After"])
    assert 0 < retry_after <= 60
    assert float(rejected.headers["X-RateLimit-Reset"]) > 0
    # The rejection is the documented JSON envelope, never a traceback.
    assert "traceback" not in rejected.text.lower()


def test_in625_h2_sg32_window_expiry_restores_capacity(restore_limiter):
    _, clock = _enable(requests=2, window=10.0)
    client = _client()

    assert _evaluate(client).status_code == 200
    assert _evaluate(client).status_code == 200
    assert _evaluate(client).status_code == 429

    clock.advance(9.9)
    assert _evaluate(client).status_code == 429

    clock.advance(0.2)
    recovered = _evaluate(client)
    assert recovered.status_code == 200
    assert recovered.headers["X-RateLimit-Remaining"] == "1"


def test_in625_h2_sg32_health_and_schema_endpoints_are_exempt(restore_limiter):
    """/health, /docs and /openapi.json must stay reachable when limiting."""
    _enable(requests=1)
    client = _client()

    assert _evaluate(client).status_code == 200
    assert _evaluate(client).status_code == 429

    assert client.get("/api/v1/health").status_code == 200
    assert client.get("/api/v1/health").status_code == 200
    assert client.get("/api/v1/openapi.json").status_code == 200
    assert client.get("/api/v1/docs").status_code == 200


def test_in625_h2_sg32_cors_preflight_is_not_throttled(restore_limiter):
    """A throttled preflight would surface as a CORS error, not a 429."""
    _enable(requests=1)
    client = _client()

    assert _evaluate(client).status_code == 200
    assert _evaluate(client).status_code == 429

    preflight = client.options(
        "/api/v1/evaluate",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert preflight.status_code != 429
    assert "Retry-After" not in preflight.headers


def test_in625_h2_sg32_buckets_are_per_client(restore_limiter):
    _enable(requests=1)
    first = _client(("203.0.113.10", 50000))
    second = _client(("203.0.113.11", 50000))

    assert _evaluate(first).status_code == 200
    assert _evaluate(first).status_code == 429
    assert _evaluate(second).status_code == 200


def test_in625_h2_sg32_forwarded_for_is_ignored_by_default(restore_limiter):
    """A spoofed X-Forwarded-For must not buy a fresh bucket by default."""
    _enable(requests=1, trust_forwarded_for=False)
    client = _client()

    assert _evaluate(client, {"X-Forwarded-For": "198.51.100.1"}).status_code == 200
    assert _evaluate(client, {"X-Forwarded-For": "198.51.100.2"}).status_code == 429


def test_in625_h2_sg32_forwarded_for_is_honored_only_when_trusted(restore_limiter):
    _enable(requests=1, trust_forwarded_for=True)
    client = _client()

    assert _evaluate(client, {"X-Forwarded-For": "198.51.100.1"}).status_code == 200
    assert _evaluate(
        client, {"X-Forwarded-For": "198.51.100.1"}
    ).status_code == 429
    assert _evaluate(client, {"X-Forwarded-For": "198.51.100.2"}).status_code == 200
    # Comma chains keep the left-most (client) entry.
    assert _evaluate(
        client, {"X-Forwarded-For": "198.51.100.3, 10.0.0.1"}
    ).status_code == 200
    assert _evaluate(
        client, {"X-Forwarded-For": "198.51.100.3, 10.0.0.9"}
    ).status_code == 429


def test_in625_h2_sg32_tracked_keys_are_bounded(restore_limiter):
    """Memory does not grow without bound when many clients appear."""
    limiter = FixedWindowRateLimiter(
        requests=1, window_seconds=60.0, max_tracked_clients=3
    )

    for index in range(10):
        limiter.check(f"192.0.2.{index}")
    assert limiter.tracked_clients <= 3

    # Eviction must not resurrect an unlimited bucket for an evicted client.
    assert limiter.check("192.0.2.9").allowed is False


def test_in625_h2_sg32_invalid_configuration_is_rejected():
    with pytest.raises(ValueError):
        FixedWindowRateLimiter(requests=-1, window_seconds=60.0)
    with pytest.raises(ValueError):
        FixedWindowRateLimiter(requests=1, window_seconds=0)


def test_in625_h2_sg32_exemptions_match_exact_paths_only():
    """User traffic must not inherit an exemption from its suffix."""
    from app.services.rate_limit import is_exempt_path

    assert is_exempt_path("/api/v1/health") is True
    assert is_exempt_path("/api/v1/docs") is True
    assert is_exempt_path("/api/v1/openapi.json") is True
    assert is_exempt_path("/api/v1/algebra/docs") is False
    assert is_exempt_path("/api/v1/evaluate/openapi.json") is False
    assert is_exempt_path("/health") is False


def test_in625_h2_sg32_settings_read_the_environment(monkeypatch):
    from app.core.config import Settings

    monkeypatch.setenv("RATE_LIMIT_REQUESTS", "7")
    monkeypatch.setenv("RATE_LIMIT_WINDOW_SECONDS", "2.5")
    monkeypatch.setenv("RATE_LIMIT_TRUST_FORWARDED_FOR", "true")
    settings = Settings()
    assert settings.rate_limit_requests == 7
    assert settings.rate_limit_window_seconds == 2.5
    assert settings.rate_limit_trust_forwarded_for is True

    monkeypatch.delenv("RATE_LIMIT_REQUESTS")
    monkeypatch.delenv("RATE_LIMIT_WINDOW_SECONDS")
    monkeypatch.delenv("RATE_LIMIT_TRUST_FORWARDED_FOR")
    defaults = Settings()
    assert defaults.rate_limit_requests == 0
    assert defaults.rate_limit_window_seconds == 60.0
    assert defaults.rate_limit_trust_forwarded_for is False
