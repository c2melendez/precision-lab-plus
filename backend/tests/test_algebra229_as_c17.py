"""Algebra229 AS-C-17 gcd(x^2-1, x^2-2x+1): frozen row, expected x-1."""
import gzip
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"
INPUT = "gcd(x^2-1, x^2-2*x+1)"


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


def test_as_c17_source_row_matches_all_frozen_contract_cells():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-C-17 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert len(cells) == 8, source_row
    assert cells[1:7] == [
        "AS-C-17",
        "N2",
        "`valor`",
        r"`\gcd\left(x^{2}-1,\ x^{2}-2x+1\right)`",
        "`x - 1`",
        "",
    ], source_row
    assert cells[7] == "", source_row


def test_as_c17_evaluate_gcd_is_equivalent_to_x_minus_1():
    x = sp.Symbol("x")
    result = _evaluate(INPUT)
    assert result["success"] is True, result
    engine = sp.sympify(result["result_text"].replace("^", "**"), locals={"x": x})
    assert sp.simplify(engine - (x - 1)) == 0, result


def test_as_c17_simplify_gcd_is_equivalent_to_x_minus_1():
    x = sp.Symbol("x")
    result = _simplify(INPUT)
    engine = sp.sympify(result["result_text"].replace("^", "**"), locals={"x": x})
    assert sp.simplify(engine - (x - 1)) == 0, result


def test_as_c17_independent_shared_root_x_equals_1():
    assert (1**2 - 1) == 0
    assert (1**2 - 2 * 1 + 1) == 0


def test_as_c17_x_plus_1_divides_first_but_not_second():
    assert ((-1) ** 2 - 1) == 0
    assert ((-1) ** 2 - 2 * (-1) + 1) != 0
