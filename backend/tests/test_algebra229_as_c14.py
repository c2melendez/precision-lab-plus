"""Algebra229 AS-C-14 division (x^4-1) by (x^2+1): frozen row, exact quotient x^2-1, remainder 0."""
import gzip
from fractions import Fraction
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"
INPUT = "(x^4-1)/(x^2+1)"
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


def test_as_c14_source_row_matches_all_frozen_contract_cells():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-C-14 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert len(cells) == 8, source_row
    assert cells[1:7] == [
        "AS-C-14",
        "N2",
        "`division`",
        r"`\left(x^{4}-1\right)\div\left(x^{2}+1\right)`",
        r"`q=x^{2} - 1,\ r=0`",
        "",
    ], source_row
    assert cells[7] == "", source_row


def test_as_c14_exact_polynomial_identity_holds():
    for x in SAMPLES:
        assert x**4 - 1 == (x * x + 1) * (x * x - 1) + 0


def test_as_c14_simplify_endpoint_is_equivalent_to_exact_quotient():
    x = sp.Symbol("x")
    result = _simplify(INPUT)
    engine = sp.sympify(result["result_text"].replace("^", "**"), locals={"x": x})
    assert sp.simplify(engine - (x**2 - 1)) == 0, result


def test_as_c14_independent_arithmetic_matches_every_sample():
    for x in SAMPLES:
        expected = Fraction(x**4 - 1, x * x + 1)
        assert expected == Fraction(x * x - 1)
        result = _evaluate(f"(x^4-1)/(x^2+1) con x={x}")
        assert result["success"] is True, result
        assert Fraction("".join(result["result_text"].split())) == expected, (x, result)


def test_as_c14_remainder_is_identically_zero():
    for x in SAMPLES:
        left = x**4 - 1
        right = (x * x + 1) * (x * x - 1)
        assert left - right == 0
