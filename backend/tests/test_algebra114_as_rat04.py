"""Algebra114 AS-RAT-04 original cube-root denominator rationalization."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.algebra_service import simplify_expression


def test_as_rat_04_cube_root_denominator_service_http():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-RAT-04 | N2 |" in source
    original = "1/(2**(1/3))"
    expected = sp.real_root(4, 3)/2
    result = simplify_expression(original)
    assert sp.simplify(result.result_expr - expected) == 0
    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": original})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    assert sp.simplify(sp.sympify(payload["result_text"]) - expected) == 0
