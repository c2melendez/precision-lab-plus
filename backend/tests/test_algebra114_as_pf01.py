"""AS-PF-01: simple-pole decomposition with service, HTTP, and Fraction oracle."""
from fractions import Fraction
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app
from app.services.algebra_service import partial_fraction_expression


def test_as_pf_01_exact_partial_fractions_service_http_fraction_oracle():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert r"| AS-PF-01 | N2 | \( \frac{3x+5}{(x+1)(x+2)} \) | \( \frac{2}{x+1}+\frac{1}{x+2} \) |".replace(" ", "") in source.replace(" ", "")

    x = sp.Symbol("x")
    original = "(3*x+5)/((x+1)*(x+2))"
    expected = 2/(x+1) + 1/(x+2)
    service = partial_fraction_expression(original, "x")
    assert sp.cancel(service.result_expr - expected) == 0
    assert service.result_expr != service.input_expr
    assert sp.apart(service.result_expr, x) == expected

    with TestClient(app) as client:
        response = client.post("/api/v1/partial-fractions", json={"expression": original})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    actual = sp.sympify(payload["result_text"])
    assert sp.cancel(actual - expected) == 0

    # Exact arithmetic oracle independent of SymPy.
    for value in [-5, -4, -3, 0, 1, 3, 4, 5]:
        oracle = Fraction(2, value+1) + Fraction(1, value+2)
        original_oracle = Fraction(3*value+5, (value+1)*(value+2))
        assert oracle == original_oracle
        expected_exact = sp.Rational(oracle.numerator, oracle.denominator)
        assert sp.cancel(service.result_expr.subs(x, value) - expected_exact) == 0
        assert sp.cancel(actual.subs(x, value) - expected_exact) == 0
