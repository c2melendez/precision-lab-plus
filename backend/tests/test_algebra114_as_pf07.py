"""AS-PF-07 numerator x with two irreducible quadratic factors via service/HTTP."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.algebra_service import partial_fraction_expression


def test_as_pf_07_linear_numerator_quadratic_factors_service_http():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-PF-07 | N3 |" in source
    x = sp.Symbol("x")
    original = "x/((x**2+1)*(x**2+4))"
    expected = x/(3*(x*x+1))-x/(3*(x*x+4))
    service = partial_fraction_expression(original)
    assert sp.cancel(service.result_expr - expected) == 0
    assert service.result_expr.is_Add and len(service.result_expr.args) == 2
    with TestClient(app) as client:
        response = client.post("/api/v1/partial-fractions", json={"expression": original})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    actual = sp.sympify(payload["result_text"])
    assert actual.is_Add and len(actual.args) == 2
    assert sp.cancel(actual-expected) == 0
