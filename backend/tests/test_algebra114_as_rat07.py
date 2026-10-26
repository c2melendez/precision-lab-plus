"""AS-RAT-07 original nested radical denesting through service and HTTP."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.algebra_service import simplify_expression


def test_as_rat_07_nested_radical_denesting_service_http():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-RAT-07 | N3 |" in source
    original = "sqrt(2+sqrt(3))"
    expected = (sp.sqrt(6) + sp.sqrt(2)) / 2

    service = simplify_expression(original)
    assert service.result_expr == expected
    assert abs(float(sp.N(service.result_expr)) - float(sp.N(expected))) < 1e-12

    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": original})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    assert sp.sympify(payload["result_text"]) == expected
