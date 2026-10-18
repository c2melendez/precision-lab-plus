"""AS-PF-03 exact decomposition with irreducible quadratic factor."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.algebra_service import partial_fraction_expression


def test_as_pf_03_linear_and_irreducible_quadratic_service_http():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-PF-03 | N2 |" in source
    x = sp.Symbol("x")
    expected = 1/x + (1-x)/(x*x+1)
    expr = "(x+1)/(x*(x**2+1))"
    service = partial_fraction_expression(expr)
    assert sp.cancel(service.result_expr - expected) == 0
    assert service.result_expr.is_Add and len(service.result_expr.args) == 2
    with TestClient(app) as client:
        response = client.post("/api/v1/partial-fractions", json={"expression": expr})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    actual = sp.sympify(payload["result_text"])
    assert sp.cancel(actual - expected) == 0
    assert actual.is_Add and len(actual.args) == 2
