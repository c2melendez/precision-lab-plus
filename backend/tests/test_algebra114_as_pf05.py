"""AS-PF-05 improper fraction: exact quotient and original domain exclusions."""
from fractions import Fraction
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app
from app.services.algebra_service import partial_fraction_expression


def test_as_pf_05_improper_fraction_service_http_and_original_domain():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-PF-05 | N3 | \\(\\frac{x^{3}+1}{x^{2}-1}\\) | \\(x+\\frac{1}{x-1}\\), con \\(x\\neq\\pm1\\) |" in source

    x = sp.Symbol("x")
    original = "(x**3+1)/(x**2-1)"
    expected = x+1/(x-1)
    domain_exclusions = {sp.Integer(-1), sp.Integer(1)}
    # Preserve the original domain, not the domain of the cancelled expression.
    assert set(sp.solve(sp.denom(sp.sympify(original)), x)) == domain_exclusions
    original_denominator = lambda value: value*value-1
    assert original_denominator(-1) == 0
    assert original_denominator(1) == 0

    service = partial_fraction_expression(original)
    assert sp.cancel(service.result_expr-expected) == 0
    with TestClient(app) as client:
        response = client.post("/api/v1/partial-fractions", json={"expression": original})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    actual = sp.sympify(payload["result_text"])
    assert sp.cancel(actual-expected) == 0

    # Independent Fraction oracle confirms the simplified quotient on its domain;
    # original exclusions remain x = ±1 even after cancelling the factor x+1.
    for value in [-4, -2, 0, 2, 3, 5]:
        assert original_denominator(value) != 0
        simplified_oracle = Fraction(value, 1) + Fraction(1, value-1)
        original_oracle = Fraction(value**3+1, value**2-1)
        assert simplified_oracle == original_oracle
        expected_exact = sp.Rational(simplified_oracle.numerator, simplified_oracle.denominator)
        assert sp.cancel(service.result_expr.subs(x, value) - expected_exact) == 0
        assert sp.cancel(actual.subs(x, value) - expected_exact) == 0
