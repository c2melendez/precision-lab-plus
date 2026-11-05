"""AS-PF-04 original distinct real-pole decomposition, service and HTTP."""
from fractions import Fraction
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app
from app.services.algebra_service import partial_fraction_expression


def test_as_pf_04_distinct_positive_negative_poles_service_http():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-PF-04 | N2 | \\(\\frac{2x+3}{x^{2}-4}\\) | \\(\\frac{7}{4(x-2)}+\\frac{1}{4(x+2)}\\) |" in source

    x = sp.Symbol("x")
    expected = sp.Rational(7, 4)/(x-2) + sp.Rational(1, 4)/(x+2)
    original = "(2*x+3)/(x**2-4)"
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

    # Independent exact arithmetic excludes both real poles x = ±2.
    for value in [-5, -3, -1, 0, 1, 3, 5, 6]:
        oracle = Fraction(2*value+3, value*value-4)
        expected_exact = sp.Rational(oracle.numerator, oracle.denominator)
        assert sp.cancel(service.result_expr.subs(x, value) - expected_exact) == 0
        assert sp.cancel(actual.subs(x, value) - expected_exact) == 0
