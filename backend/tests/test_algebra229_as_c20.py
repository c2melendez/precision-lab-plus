"""Algebra229 AS-C-20 gcd(48,180): frozen row and exact integer GCD."""
import gzip
import math
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"
INPUT = "gcd(48,180)"
EXPECTED = "12"


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


def test_as_c20_source_row_matches_all_frozen_contract_cells():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-C-20 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert len(cells) == 8, source_row
    assert cells[1:7] == [
        "AS-C-20",
        "N1",
        "`valor`",
        r"`\gcd(48,180)`",
        "`12`",
        "",
    ], source_row
    assert cells[7] == "", source_row


def test_as_c20_evaluate_gcd_returns_frozen_exact_value_12():
    result = _evaluate(INPUT)
    assert result["success"] is True, result
    engine = sp.sympify(result["result_text"].replace("^", "**"))
    expected = sp.Integer(12)
    assert sp.simplify(engine - expected) == 0, result


def test_as_c20_simplify_gcd_returns_frozen_exact_value_12():
    result = _simplify(INPUT)
    engine = sp.sympify(result["result_text"].replace("^", "**"))
    assert sp.simplify(engine - sp.Integer(12)) == 0, result


def test_as_c20_independent_integer_gcd_and_divisibility():
    assert math.gcd(48, 180) == 12
    assert 48 % 12 == 0
    assert 180 % 12 == 0
    assert math.gcd(48, 180) > 1
