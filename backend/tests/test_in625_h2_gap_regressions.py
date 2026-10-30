"""IN625 H2 gap regressions tied to the primary EN-SG contract.

These are bounded CI tests. They must never be invoked against a deployed service.
A safe-rejection assertion is explicitly not acceptance of EN-SG-21's value oracle.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)


@pytest.mark.timeout(15, method="signal")
def test_en_sg_21_ten_thousand_terms_preserves_current_request_limit_contract():
    """Document the known contract conflict without weakening the 500-char limit."""
    expression = "+".join(["1"] * 10_000)
    response = client.post(
        "/api/v1/evaluate",
        json={"expression": expression, "angle_unit": "rad"},
    )
    assert response.status_code == 422, response.text[:250]
    body = response.json()
    assert body.get("success") is False, body
    assert body.get("error_code") == "VALIDATION_ERROR", body
    assert body.get("request_id"), body
    assert response.headers.get("x-request-id") == body["request_id"]
    # This is a controlled-rejection regression, not EN-SG-21 acceptance:
    # the normative oracle asks for 10000, but the public expression limit is 500.


@pytest.mark.timeout(15, method="signal")
def test_en_sg_25_million_factorial_is_bounded_and_returns_a_clear_contract(monkeypatch):
    """Keep the million-factorial stress input inside the opt-in child-process budget."""
    monkeypatch.setenv("SG28_EVALUATE_ISOLATION", "1")
    monkeypatch.setenv("SG28_ISOLATED_CPU_SECONDS", "1")
    monkeypatch.delenv("SG28_ISOLATED_MEMORY_MB", raising=False)

    response = client.post(
        "/api/v1/evaluate",
        json={"expression": "1000000!", "angle_unit": "rad"},
    )
    assert response.status_code != 500, response.text[:300]
    body = response.json()
    assert body.get("request_id"), body
    assert body.get("operation") == "evaluate", body
    assert "traceback" not in response.text.lower()
    if body.get("success") is True:
        # The renderer must not serialize millions of digits into the response.
        assert body.get("result_latex") is None, body
        message = str(body.get("result_text") or "").lower()
        warnings = " ".join(map(str, body.get("warnings") or [])).lower()
        assert "demasiado grande" in message or "demasiado grande" in warnings, body
    else:
        assert body.get("error_code") in {"TIMEOUT", "COMPLEXITY_LIMIT"}, body
        assert str(body.get("error_message") or "").strip(), body


@pytest.mark.timeout(20, method="signal")
def test_en_sg_26_expand_ten_thousand_power_returns_complexity_limit():
    """The large expansion is allowed only in CI and must stop at the node guard."""
    response = client.post(
        "/api/v1/expand",
        json={"expression": "(x+1)**10000"},
    )
    assert response.status_code == 200, response.text[:300]
    body = response.json()
    assert body.get("success") is False, body
    assert body.get("error_code") == "COMPLEXITY_LIMIT", body
    assert str(body.get("error_message") or "").strip(), body
    assert "traceback" not in response.text.lower()


@pytest.mark.timeout(15, method="signal")
def test_en_sg_27_five_level_power_tower_is_symbolic_or_clearly_bounded():
    """The 2^65536 case may be represented exactly or rejected with a clear limit."""
    response = client.post(
        "/api/v1/evaluate",
        json={"expression": "2**(2**(2**(2**2)))", "angle_unit": "rad"},
    )
    assert response.status_code != 500, response.text[:300]
    body = response.json()
    assert body.get("request_id"), body
    if body.get("success") is False:
        assert body.get("error_code") in {"TIMEOUT", "COMPLEXITY_LIMIT"}, body
        assert str(body.get("error_message") or "").strip(), body
    else:
        result_text = str(body.get("result_text") or "").lower()
        warnings = " ".join(map(str, body.get("warnings") or [])).lower()
        assert (
            "65536" in result_text
            or "demasiado grande" in result_text
            or "demasiado grande" in warnings
        ), body
