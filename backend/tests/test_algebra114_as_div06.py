"""AS-DIV-06: original cubic division by a quadratic, with exact quotient and HTTP."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.algebra_service import simplify_expression


def test_as_div_06_original_cubic_division_service_http():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-DIV-06 | N3 |" in source
    x = sp.Symbol("x")
    numerator, denominator = x**3+1, x**2-x+1
    quotient_expected, remainder_expected = x+1, sp.Integer(0)
    quotient, remainder = sp.div(numerator, denominator, x)
    assert sp.expand(quotient-quotient_expected) == 0
    assert remainder == remainder_expected
    assert sp.expand(numerator-denominator*quotient-remainder) == 0
    expected = quotient_expected
    service = simplify_expression("(x**3+1)/(x**2-x+1)")
    assert sp.simplify(service.result_expr-expected) == 0
    for xx in (-3, -1, 0, 1, 2, 4):
        assert abs(float(sp.N(service.result_expr.subs(x, xx)))-float(sp.N(expected.subs(x, xx)))) < 1e-9
    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": "(x**3+1)/(x**2-x+1)"})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    assert sp.simplify(sp.sympify(payload["result_text"])-expected) == 0
