"""Algebra229 AS-A-15 expansion with exact rational samples (x != 0)."""
import gzip
from fractions import Fraction
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app
from app.services.algebra_service import expand_expression

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"


def test_as_a15_source_row_is_exact():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-A-15 |"))
    expected_row = r"| AS-A-15 | N3 | `expandir` | `\left(x+\frac{1}{x}\right)^{3}` | `x^{3} + 3 x + \frac{3}{x} + \frac{1}{x^{3}}` | Exponentes negativos tras expandir. |"
    assert source_row == expected_row


def test_as_a15_expand_service_http_and_independent_fraction_oracle():
    original = "(x+1/x)^3"
    x = sp.symbols("x")
    symbolic_oracle = x**3 + 3 * x + 3 / x + 1 / x**3

    service = expand_expression(original)
    assert sp.simplify(service.result_expr - symbolic_oracle) == 0

    with TestClient(app) as client:
        response = client.post("/api/v1/expand", json={"expression": original})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    http_expr = sp.sympify(payload["result_text"])
    assert sp.simplify(http_expr - symbolic_oracle) == 0
    assert "(x+1/x)**3" not in payload["result_text"].replace(" ", "")

    # Exact Python Fraction arithmetic is independent from SymPy simplification.
    samples = (
        Fraction(-3), Fraction(-2), Fraction(-1, 2), Fraction(1, 4),
        Fraction(1), Fraction(2), Fraction(5),
    )
    for value in samples:
        exact_x = sp.Rational(value.numerator, value.denominator)
        expected = value**3 + 3 * value + Fraction(3, 1) / value + Fraction(1, 1) / value**3
        exact_expected = sp.Rational(expected.numerator, expected.denominator)
        assert service.result_expr.subs(x, exact_x) == exact_expected
        assert http_expr.subs(x, exact_x) == exact_expected
