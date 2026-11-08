"""Algebra229 AS-C-18 lcm(x^2-1, x^2-2x+1): frozen row, expected (x-1)^2 (x+1)."""
import gzip
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"
INPUT = "lcm(x^2-1, x^2-2*x+1)"
EXPECTED = "(x-1)**2 * (x+1)"


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


def test_as_c18_source_row_matches_all_frozen_contract_cells():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-C-18 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert len(cells) == 8, source_row
    assert cells[1:7] == [
        "AS-C-18",
        "N2",
        "`valor`",
        r"`\operatorname{lcm}\left(x^{2}-1,\ x^{2}-2x+1\right)`",
        r"`\left(x - 1\right)^{2} \left(x + 1\right)`",
        "",
    ], source_row
    assert cells[7] == "", source_row


def test_as_c18_evaluate_lcm_is_equivalent_to_expected():
    x = sp.Symbol("x")
    result = _evaluate(INPUT)
    assert result["success"] is True, result
    engine = sp.sympify(result["result_text"].replace("^", "**"), locals={"x": x})
    expected = sp.sympify(EXPECTED, locals={"x": x})
    assert sp.simplify(engine - expected) == 0, result


def test_as_c18_simplify_lcm_is_equivalent_to_expected():
    x = sp.Symbol("x")
    result = _simplify(INPUT)
    engine = sp.sympify(result["result_text"].replace("^", "**"), locals={"x": x})
    expected = sp.sympify(EXPECTED, locals={"x": x})
    assert sp.simplify(engine - expected) == 0, result


def test_as_c18_lcm_times_gcd_equals_product():
    x = sp.Symbol("x")
    f = x**2 - 1
    g = x**2 - 2 * x + 1
    lcm_r = _evaluate(INPUT)
    gcd_r = _evaluate("gcd(x^2-1, x^2-2*x+1)")
    assert lcm_r["success"] and gcd_r["success"], (lcm_r, gcd_r)
    lcm_e = sp.sympify(lcm_r["result_text"].replace("^", "**"), locals={"x": x})
    gcd_e = sp.sympify(gcd_r["result_text"].replace("^", "**"), locals={"x": x})
    assert sp.simplify(lcm_e * gcd_e - f * g) == 0


def test_as_c18_expected_vanishes_at_shared_roots():
    assert ((1 - 1) ** 2 * (1 + 1)) == 0
    assert ((-1 - 1) ** 2 * (-1 + 1)) == 0
