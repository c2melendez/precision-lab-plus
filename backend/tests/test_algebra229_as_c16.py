"""Algebra229 AS-C-16 division (x^5-1) by (x-1): frozen row, q=x^4+x^3+x^2+x+1, r=0."""
import gzip
from fractions import Fraction
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"
INPUT = "(x^5-1)/(x-1)"
SAMPLES = (-3, -2, -1, 0, 2, 3, 4)  # exclude x=1


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


def test_as_c16_source_row_matches_all_frozen_contract_cells():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-C-16 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert len(cells) == 8, source_row
    assert cells[1:7] == [
        "AS-C-16",
        "N2",
        "`division`",
        r"`\left(x^{5}-1\right)\div(x-1)`",
        r"`q=x^{4} + x^{3} + x^{2} + x + 1,\ r=0`",
        "",
    ], source_row
    assert cells[7] == "", source_row


def test_as_c16_exact_polynomial_identity_holds():
    for x in SAMPLES:
        assert x**5 - 1 == (x - 1) * (x**4 + x**3 + x**2 + x + 1)


def test_as_c16_simplify_endpoint_is_equivalent_to_geometric_sum():
    x = sp.Symbol("x")
    result = _simplify(INPUT)
    engine = sp.sympify(result["result_text"].replace("^", "**"), locals={"x": x})
    assert sp.simplify(engine - (x**4 + x**3 + x**2 + x + 1)) == 0, result


def test_as_c16_independent_arithmetic_matches_every_sample_with_x_not_1():
    for x in SAMPLES:
        expected = Fraction(x**5 - 1, x - 1)
        assert expected == Fraction(x**4 + x**3 + x**2 + x + 1)
        result = _evaluate(f"(x^5-1)/(x-1) con x={x}")
        assert result["success"] is True, result
        assert Fraction("".join(result["result_text"].split())) == expected, (x, result)


def test_as_c16_excluded_point_x_equals_1_is_domain_error():
    result = _evaluate("(x^5-1)/(x-1) con x=1")
    assert result["success"] is False, result
    assert result["error_code"] == "DOMAIN_ERROR", result
