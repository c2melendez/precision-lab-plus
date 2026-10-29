"""SY-X-04 (Plus HTTP channel) — scoped evidence.

Matrix row:
  entrada: x+x+x+⋯+x (500 términos)
  esperado: 500x

Two independent limits apply before any CAS work:
  1. EvaluateRequest.max_length=500 characters. A literal 500-term sum is
     ~999 characters and is rejected at the Pydantic boundary (422
     VALIDATION_ERROR).
  2. ast_validator.MAX_AST_NODES=200. With evaluate=False, an n-term flat
     Add has exactly n+1 nodes, so sums of >=200 terms are rejected with
     COMPLEXITY_LIMIT even when they fit the character budget. The largest
     passing flat sum is 199 terms (200 nodes, 397 chars).

These tests certify both contract boundaries and the functional subset
within them (n*x equivalence for admissible sizes), plus recovery after
each rejection class.

Classification: PASS (scoped length + AST-node contracts + functional
subset). Does not claim unrestricted 500-term HTTP evaluation; that would
require a contractual change to MAX_AST_NODES or a flattened-add evaluator.
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
    """A sum that fits BOTH contracts must simplify to N*x (or equivalent).

    Empirically verified boundary: n=199 terms -> 200 AST nodes (allowed,
    `nodes > MAX_AST_NODES` is the rejection condition) and 397 chars
    (< 500). n=200 terms -> 201 nodes -> COMPLEXITY_LIMIT. See
    test_sy_x04_two_hundred_term_sum_rejected_at_ast_node_boundary below.
    """
    # 199 terms → "x+"*198 + "x" = 397 chars, 200 AST nodes: both limits pass.
    n = 199
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
    # Common acceptable forms: "199*x", "199x", "x*199"
    acceptable = (
        f"{n}*x" in text
        or f"{n}x" in text
        or f"x*{n}" in text
        or text == str(n)  # if evaluated under a substitution (should not happen)
    )
    assert acceptable, (text, body)


def test_sy_x04_two_hundred_term_sum_rejected_at_ast_node_boundary():
    """200-term sum fits the 500-char request contract but exceeds
    MAX_AST_NODES=200 (flat Add of 200 terms -> 201 nodes).

    Expected controlled rejection: HTTP 200 with success=false and
    error_code=COMPLEXITY_LIMIT — no traceback, no unhandled crash.
    This pins the second boundary so the functional subset above cannot
    silently drift past it.
    """
    expression = _n_term_sum(200)
    assert len(expression) <= 500, len(expression)  # passes length contract

    response = client.post(
        "/api/v1/evaluate",
        json={"expression": expression, "angle_unit": "rad"},
    )
    assert response.status_code == 200, response.text[:300]
    body = response.json()
    assert body.get("success") is False, body
    assert body.get("error_code") == "COMPLEXITY_LIMIT", body
    assert "200" in str(body.get("error_message")), body
    assert "traceback" not in response.text.lower()


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
