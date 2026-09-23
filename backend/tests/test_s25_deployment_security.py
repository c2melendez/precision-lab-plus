from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)
ORIGIN = "https://security-test.example"


def _assert_security_headers(response):
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"
    assert response.headers["x-frame-options"] == "DENY"


def test_s25_success_response_has_security_headers():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    _assert_security_headers(response)
    assert "default-src 'none'" in response.headers.get("content-security-policy", "")


def test_s25_validation_error_preserves_cors_and_security_headers():
    response = client.post(
        "/api/v1/evaluate",
        json={},
        headers={"Origin": ORIGIN},
    )
    assert response.status_code == 422
    assert response.headers.get("access-control-allow-origin") == ORIGIN
    _assert_security_headers(response)


def test_s25_not_found_preserves_cors_and_security_headers():
    response = client.get(
        "/api/v1/route-that-does-not-exist",
        headers={"Origin": ORIGIN},
    )
    assert response.status_code == 404
    assert response.headers.get("access-control-allow-origin") == ORIGIN
    _assert_security_headers(response)


def test_s25_trig_domain_error_never_escapes_as_500():
    response = client.post(
        "/api/v1/evaluate",
        json={"expression": "sec(pi/2)", "angle_unit": "rad"},
        headers={"Origin": ORIGIN},
    )
    assert response.status_code != 500
    body = response.json()
    assert body["success"] is False
    assert body["error_code"] == "DOMAIN_ERROR"
    assert response.headers.get("access-control-allow-origin") == ORIGIN
    _assert_security_headers(response)
