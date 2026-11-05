"""AS-PF-02: repeated-pole decomposition with service, HTTP, and Fraction oracle."""
from fractions import Fraction
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app
from app.services.algebra_service import partial_fraction_expression


def test_as_pf_02_repeated_pole_service_http_fraction_oracle():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert r"| AS-PF-02 | N2 | \( \frac{1}{x(x-1)^{2}} \) | \( \frac{1}{x}-\frac{1}{x-1}+\frac{1}{(x-1)^{2}} \) |".replace(" ", "") in source.replace(" ", "")

    x = sp.Symbol("x")
    original = "1/(x*(x-1)**2)"
    expected = 1/x - 1/(x-1) + 1/(x-1)**2
    service = partial_fraction_expression(original)
    assert sp.cancel(service.result_expr - expected) == 0
    assert service.result_expr.is_Add and len(service.result_expr.args) == 3

    with TestClient(app) as client:
        response = client.post("/api/v1/partial-fractions", json={"expression": original})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    actual = sp.sympify(payload["result_text"])
    assert actual.is_Add and len(actual.args) == 3
    assert sp.cancel(actual - expected) == 0

    for value in [-5, -4, -2, 2, 3, 5, 7, 8]:
        oracle = Fraction(1, value) - Fraction(1, value-1) + Fraction(1, (value-1)**2)
        original_oracle = Fraction(1, value*(value-1)**2)
        assert oracle == original_oracle
        expected_exact = sp.Rational(oracle.numerator, oracle.denominator)
        assert sp.cancel(service.result_expr.subs(x, value) - expected_exact) == 0
        assert sp.cancel(actual.subs(x, value) - expected_exact) == 0
