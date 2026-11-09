"""Algebra229 AS-C-22 remainder of x^100-1 by x-1: frozen row and exact remainder theorem."""
import gzip
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"
INPUT = "x^100-1"
QUOTIENT = "(x^100-1)/(x-1)"


def _evaluate(expression: str, substitutions: dict[str, str] | None = None) -> dict:
    payload: dict = {"expression": expression}
    if substitutions is not None:
        payload["substitutions"] = substitutions
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json=payload)
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    assert result["request_id"], result
    return result


def _exact(text: str) -> sp.Expr:
    return sp.sympify(text.replace("^", "**"))


def test_as_c22_source_row_matches_all_frozen_contract_cells():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-C-22 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert len(cells) == 8, source_row
    assert cells[1:7] == [
        "AS-C-22",
        "N2",
        "`valor`",
        r"`\text{resto de }x^{100}-1\ \text{entre}\ x-1`",
        "`0`",
        "Teorema del resto: `p(1)=0`.",
    ], source_row
    assert cells[7] == "", source_row


def test_as_c22_remainder_theorem_p_at_1_is_zero():
    result = _evaluate(INPUT, {"x": "1"})
    assert _exact(result["result_text"]) == 0, result


def test_as_c22_quotient_at_2_is_exact_two_to_100_minus_1():
    result = _evaluate(QUOTIENT, {"x": "2"})
    assert _exact(result["result_text"]) == sp.Integer(2) ** 100 - 1, result


def test_as_c22_independent_geometric_oracle_confirms_exact_division():
    # (x^100-1) = (x-1)*(1+x+...+x^99); at x=2 the quotient is the geometric sum.
    geometric = sum(2 ** k for k in range(100))
    assert geometric == 2 ** 100 - 1
    _, remainder = divmod(2 ** 100 - 1, 2 - 1)
    assert remainder == 0
    assert 1 ** 100 - 1 == 0
