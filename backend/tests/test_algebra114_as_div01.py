"""Algebra114 AS-DIV-01 original quotient, remainder and removable hole."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.algebra_service import simplify_expression


def test_as_div_01_original_polynomial_quotient_and_domain():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-DIV-01 | N1 |" in source
    x = sp.Symbol("x")
    numerator, denominator = x**2-4, x-2
    quotient, remainder = sp.div(numerator, denominator, x)
    assert sp.expand(quotient-(x+2)) == 0
    assert remainder == 0
    assert sp.simplify(numerator-denominator*quotient-remainder) == 0
    assert denominator.subs(x, 2) == 0  # Original input excludes x=2.
    service = simplify_expression("(x**2-4)/(x-2)")
    for xx in (-3, -1, 0, 1, 3, 4):
        assert abs(float(sp.N(service.result_expr.subs(x, xx)))-(xx+2)) < 1e-9
    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": "(x**2-4)/(x-2)"})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    assert sp.simplify(sp.sympify(payload["result_text"])-(x+2)) == 0
