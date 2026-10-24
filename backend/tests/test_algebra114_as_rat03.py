"""Algebra114 AS-RAT-03 original conjugate rationalization with two radicals."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.algebra_service import simplify_expression


def test_as_rat_03_two_radical_conjugate_service_http():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-RAT-03 | N2 |" in source
    expression = "1/(sqrt(2)+sqrt(3))"
    expected = sp.sqrt(3)-sp.sqrt(2)
    service = simplify_expression(expression)
    assert sp.simplify(service.result_expr-expected) == 0
    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": expression})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    assert sp.simplify(sp.sympify(payload["result_text"])-expected) == 0
