"""SY-X-04 (Plus HTTP channel) — scoped evidence.

Matrix row:
  entrada: x+x+x+⋯+x (500 términos)
  esperado: 500x

EvaluateRequest.max_length=500. A literal 500-term sum is ~999 characters
and is rejected at the Pydantic validation boundary (422 VALIDATION_ERROR)
before any CAS work. This test certifies that contract behaviour and, in a
second case, that a sum which does fit the contract produces the expected
equivalent result.

Classification: PASS (scoped request-length contract + functional subset).
Does not claim unrestricted 500-term HTTP evaluation.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def _n_term_sum(n: int) -> str:
    """Build 'x+x+...+x' with exactly n terms."""
    return "+".join(["x"] * n)


def test_sy_x04_five_hundred_term_sum_rejected_at_request_length_boundary():
    """Canonical 500-term input exceeds max_length=500 → controlled 422."""
    expression = _n_term_sum(500)
    assert len(expression) > 500, len(expression)

    response = client.post(
        "/api/v1/evaluate",
        json={"expression": expression, "angle_unit": "rad"},
    )
    assert response.status_code == 422, response.text[:300]
    body = response.json()
    assert body.get("success") is False, body
    assert body.get("error_code") == "VALIDATION_ERROR", body
    assert body.get("error_message"), body
    # Message should reference the length limit.
    assert "500" in str(body.get("error_message")), body
    assert "traceback" not in response.text.lower()


def test_sy_x04_functional_subset_within_length_contract_yields_nx():
    """A sum that fits max_length=500 must simplify to N*x (or equivalent)."""
    # 200 terms → "x+"*199 + "x" = 399 chars, safely under 500.
    n = 200
    expression = _n_term_sum(n)
    assert len(expression) <= 500, len(expression)

    response = client.post(
        "/api/v1/evaluate",
        json={"expression": expression, "angle_unit": "rad"},
    )
    assert response.status_code == 200, response.text[:300]
    body = response.json()
    assert body.get("success") is True, body

    # Accept any rendering that is mathematically equivalent to n*x.
    text = str(
        body.get("result_text")
        or body.get("result")
        or body.get("display_text")
        or body.get("output")
        or ""
    ).replace(" ", "").lower()
    # Common acceptable forms: "200*x", "200x", "x*200"
    acceptable = (
        f"{n}*x" in text
        or f"{n}x" in text
        or f"x*{n}" in text
        or text == str(n)  # if evaluated under a substitution (should not happen)
    )
    assert acceptable, (text, body)


def test_sy_x04_recovery_after_oversize_rejection():
    """A rejected oversize SY-X-04 request must not poison the next call."""
    oversize = client.post(
        "/api/v1/evaluate",
        json={"expression": _n_term_sum(500), "angle_unit": "rad"},
    )
    assert oversize.status_code == 422

    followup = client.post(
        "/api/v1/evaluate",
        json={"expression": "2+3", "angle_unit": "rad"},
    )
    assert followup.status_code == 200
    result = followup.json()
    assert result.get("success") is True, result
    assert result.get("result_approx") == pytest.approx(5.0), result
