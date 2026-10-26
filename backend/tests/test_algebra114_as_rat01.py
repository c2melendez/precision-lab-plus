"""Algebra114 AS-RAT-01 original radical rationalization via simplify HTTP."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.algebra_service import simplify_expression


def test_as_rat_01_rationalize_inverse_sqrt_two():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-RAT-01 | N1 |" in source
    expected = sp.sqrt(2) / 2
    original = "1/sqrt(2)"
    result = simplify_expression(original)
    assert result.result_expr == expected
    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": original})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    actual = sp.sympify(payload["result_text"])
    assert actual == expected
