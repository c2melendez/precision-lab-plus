"""Algebra229 AS-C-13 division (x^3+2x^2-x+3) by (x-2): frozen row, Ruffini quotient and remainder, excluded point."""
import gzip
from fractions import Fraction
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"
INPUT = "(x^3+2*x^2-x+3)/(x-2)"
SAMPLES = (-4, -1, 0, 1, 3, 5)


def _ruffini(coefficients, root):
    out = []
    carry = 0
    for c in coefficients:
        carry = carry * root + c
        out.append(carry)
    remainder = out.pop()
    return out, remainder


def _evaluate(expression: str) -> dict:
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
    assert response.status_code == 200, response.text
    return response.json()


def _simplify(expression: str) -> dict:
    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": expression})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    assert result["request_id"], result
    return result


def test_as_c13_source_row_matches_all_frozen_contract_cells():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-C-13 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert len(cells) == 8, source_row
    assert cells[1:7] == [
        "AS-C-13",
        "N2",
        "`division`",
        r"`\left(x^{3}+2x^{2}-x+3\right)\div(x-2)`",
        r"`q=x^{2} + 4 x + 7,\ r=17`",
        "Cociente y resto; coincide con la regla de Ruffini.",
    ], source_row
    assert cells[7] == "", source_row


def test_as_c13_ruffini_gives_quotient_and_remainder():
    quotient, remainder = _ruffini([1, 2, -1, 3], 2)
    assert quotient == [1, 4, 7]
    assert remainder == 17


def test_as_c13_exact_polynomial_identity_holds():
    for x in SAMPLES:
        assert x**3 + 2 * x**2 - x + 3 == (x - 2) * (x * x + 4 * x + 7) + 17


def test_as_c13_simplify_endpoint_is_equivalent_to_quotient_plus_remainder_term():
    x = sp.Symbol("x")
    result = _simplify(INPUT)
    engine = sp.sympify(result["result_text"].replace("^", "**"), locals={"x": x})
    assert sp.simplify(engine - (x**2 + 4 * x + 7 + sp.Rational(17) / (x - 2))) == 0, result


def test_as_c13_independent_arithmetic_matches_every_sample_with_x_not_equal_2():
    for x in SAMPLES:
        expected = Fraction(x**3 + 2 * x**2 - x + 3, x - 2)
        assert expected == Fraction(x * x + 4 * x + 7) + Fraction(17, x - 2)
        result = _evaluate(f"(x^3+2*x^2-x+3)/(x-2) con x={x}")
        assert result["success"] is True, result
        assert Fraction("".join(result["result_text"].split())) == expected, (x, result)


def test_as_c13_excluded_point_is_not_claimed_as_equivalent():
    result = _evaluate("(x^3+2*x^2-x+3)/(x-2) con x=2")
    assert result["success"] is False, result
    assert result["error_code"] == "DOMAIN_ERROR", result
