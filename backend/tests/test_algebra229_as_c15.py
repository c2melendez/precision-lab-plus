"""Algebra229 AS-C-15 division (2x^3+3x^2-5x+7) by (x^2+1): frozen row, q=2x+3, r=4-7x."""
import gzip
from fractions import Fraction
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"
INPUT = "(2*x^3+3*x^2-5*x+7)/(x^2+1)"
SAMPLES = (-3, -2, -1, 0, 1, 2, 3, 4)


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


def test_as_c15_source_row_matches_all_frozen_contract_cells():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-C-15 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert len(cells) == 8, source_row
    assert cells[1:7] == [
        "AS-C-15",
        "N3",
        "`division`",
        r"`\left(2x^{3}+3x^{2}-5x+7\right)\div\left(x^{2}+1\right)`",
        r"`q=2 x + 3,\ r=4 - 7 x`",
        "",
    ], source_row
    assert cells[7] == "", source_row


def test_as_c15_exact_polynomial_identity_holds():
    for x in SAMPLES:
        num = 2 * x**3 + 3 * x**2 - 5 * x + 7
        q = 2 * x + 3
        r = 4 - 7 * x
        assert num == (x * x + 1) * q + r


def test_as_c15_simplify_endpoint_is_equivalent_to_quotient_plus_remainder_term():
    x = sp.Symbol("x")
    result = _simplify(INPUT)
    engine = sp.sympify(result["result_text"].replace("^", "**"), locals={"x": x})
    expected = 2 * x + 3 + (4 - 7 * x) / (x**2 + 1)
    assert sp.simplify(engine - expected) == 0, result


def test_as_c15_independent_arithmetic_matches_every_sample():
    for x in SAMPLES:
        expected = Fraction(2 * x**3 + 3 * x**2 - 5 * x + 7, x * x + 1)
        assert expected == Fraction(2 * x + 3) + Fraction(4 - 7 * x, x * x + 1)
        result = _evaluate(f"(2*x^3+3*x^2-5*x+7)/(x^2+1) con x={x}")
        assert result["success"] is True, result
        assert Fraction("".join(result["result_text"].split())) == expected, (x, result)


def test_as_c15_remainder_is_linear_4_minus_7x():
    for x in SAMPLES:
        num = 2 * x**3 + 3 * x**2 - 5 * x + 7
        q_part = (x * x + 1) * (2 * x + 3)
        assert num - q_part == 4 - 7 * x
