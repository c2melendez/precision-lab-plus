"""Algebra114 AS-RAT-10 original rationalization, service and HTTP."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.algebra_service import simplify_expression


def test_as_rat_10_original_radical_fraction_service_http():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-RAT-10 | N3 |" in source
    original = "sqrt(3)/(sqrt(2)+sqrt(3))"
    expected = 3-sp.sqrt(6)
    service = simplify_expression(original)
    assert sp.simplify(service.result_expr-expected) == 0
    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": original})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    assert sp.simplify(sp.sympify(payload["result_text"])-expected) == 0
