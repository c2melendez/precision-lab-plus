"""Algebra229 AS-C-19 gcd(12x^2 y, 18 x y^2): frozen row, expected 6 x y."""
import gzip
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"
INPUT = "gcd(12*x^2*y, 18*x*y^2)"
EXPECTED = "6*x*y"


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


def test_as_c19_source_row_matches_all_frozen_contract_cells():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-C-19 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert len(cells) == 8, source_row
    assert cells[1:7] == [
        "AS-C-19",
        "N2",
        "`valor`",
        r"`\gcd\left(12x^{2}y,\ 18xy^{2}\right)`",
        "`6 x y`",
        "",
    ], source_row
    assert cells[7] == "", source_row


def test_as_c19_evaluate_gcd_is_equivalent_to_6xy():
    x, y = sp.symbols("x y")
    result = _evaluate(INPUT)
    assert result["success"] is True, result
    engine = sp.sympify(result["result_text"].replace("^", "**"), locals={"x": x, "y": y})
    expected = sp.sympify(EXPECTED, locals={"x": x, "y": y})
    assert sp.simplify(engine - expected) == 0, result


def test_as_c19_simplify_gcd_is_equivalent_to_6xy():
    x, y = sp.symbols("x y")
    result = _simplify(INPUT)
    engine = sp.sympify(result["result_text"].replace("^", "**"), locals={"x": x, "y": y})
    expected = sp.sympify(EXPECTED, locals={"x": x, "y": y})
    assert sp.simplify(engine - expected) == 0, result


def test_as_c19_independent_coefficient_and_degree_gcd():
    # gcd(12, 18) = 6; min degrees: x^1, y^1
    assert __import__("math").gcd(12, 18) == 6
    assert min(2, 1) == 1  # x degree
    assert min(1, 2) == 1  # y degree


def test_as_c19_divides_both_inputs():
    x, y = sp.symbols("x y")
    g = 6 * x * y
    assert sp.simplify(sp.div(12 * x**2 * y, g)[1]) == 0
    assert sp.simplify(sp.div(18 * x * y**2, g)[1]) == 0
