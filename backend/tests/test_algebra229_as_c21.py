"""Algebra229 AS-C-21 lcm(48,180): frozen row and exact integer LCM."""
import gzip
import math
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"
INPUT = "lcm(48,180)"


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


def test_as_c21_source_row_matches_all_frozen_contract_cells():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-C-21 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert len(cells) == 8, source_row
    assert cells[1:7] == [
        "AS-C-21",
        "N1",
        "`valor`",
        r"`\operatorname{lcm}(48,180)`",
        "`720`",
        "",
    ], source_row
    assert cells[7] == "", source_row


def test_as_c21_evaluate_lcm_returns_frozen_exact_value_720():
    result = _evaluate(INPUT)
    assert result["success"] is True, result
    engine = sp.sympify(result["result_text"].replace("^", "**"))
    assert sp.simplify(engine - sp.Integer(720)) == 0, result


def test_as_c21_simplify_lcm_returns_frozen_exact_value_720():
    result = _simplify(INPUT)
    engine = sp.sympify(result["result_text"].replace("^", "**"))
    assert sp.simplify(engine - sp.Integer(720)) == 0, result


def test_as_c21_independent_gcd_product_oracle_confirms_lcm():
    gcd = math.gcd(48, 180)
    lcm = abs(48 * 180) // gcd
    assert gcd == 12
    assert lcm == math.lcm(48, 180) == 720
    assert lcm % 48 == 0
    assert lcm % 180 == 0
