"""AS-PF-08: improper rational fraction and original exclusions with Fraction oracle."""
from fractions import Fraction
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app
from app.services.algebra_service import partial_fraction_expression


def test_as_pf_08_improper_fraction_service_http_domain_fraction_oracle():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert r"| AS-PF-08 | N3 | \( \frac{x^{4}}{x^{2}-1} \) | \( x^{2}+1+\frac{1}{2(x-1)}-\frac{1}{2(x+1)} \), con \( x\neq\pm1 \) |".replace(" ", "") in source.replace(" ", "")

    x = sp.Symbol("x")
    original = "x**4/(x**2-1)"
    expected = x**2+1+sp.Rational(1,2)/(x-1)-sp.Rational(1,2)/(x+1)
    domain_exclusions = {-1, 1}
    assert set(sp.solve(sp.denom(sp.sympify(original)), x)) == domain_exclusions

    service = partial_fraction_expression(original)
    assert sp.cancel(service.result_expr-expected) == 0
    assert service.result_expr.is_Add and len(service.result_expr.args) >= 3

    with TestClient(app) as client:
        response = client.post("/api/v1/partial-fractions", json={"expression": original})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    actual = sp.sympify(payload["result_text"])
    assert sp.cancel(actual-expected) == 0
    assert actual.is_Add and len(actual.args) >= 3

    for value in [-5, -3, -2, 0, 2, 3, 5]:
        assert value not in domain_exclusions
        oracle = Fraction(value*value+1, 1) + Fraction(1, 2*(value-1)) - Fraction(1, 2*(value+1))
        original_oracle = Fraction(value**4, value*value-1)
        assert oracle == original_oracle
        expected_exact = sp.Rational(oracle.numerator, oracle.denominator)
        assert sp.cancel(service.result_expr.subs(x, value)-expected_exact) == 0
        assert sp.cancel(actual.subs(x, value)-expected_exact) == 0
