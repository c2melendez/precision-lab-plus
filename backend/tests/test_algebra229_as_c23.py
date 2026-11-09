"""Algebra229 AS-C-23 p(2) with p(x)=x^3-3x+1: frozen row and exact polynomial evaluation."""
import gzip
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"
INPUT = "x^3-3*x+1"


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


def test_as_c23_source_row_matches_all_frozen_contract_cells():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-C-23 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert len(cells) == 8, source_row
    assert cells[1:7] == [
        "AS-C-23",
        "N2",
        "`valor`",
        r"`p(2)\ \text{con}\ p(x)=x^{3}-3x+1`",
        "`3`",
        "Evaluar un polinomio en un punto.",
    ], source_row
    assert cells[7] == "", source_row


def test_as_c23_evaluate_polynomial_at_2_returns_frozen_value_3():
    result = _evaluate(INPUT, {"x": "2"})
    assert _exact(result["result_text"]) == 3, result


def test_as_c23_simplify_polynomial_equals_canonical_form():
    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": INPUT})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    assert result["request_id"], result
    assert _exact(result["result_text"]) == sp.expand(sp.sympify("x**3 - 3*x + 1")), result


def test_as_c23_independent_oracle_confirms_point_evaluation():
    # Direct substitution and Horner's rule must agree, without using the engine.
    direct = 2 ** 3 - 3 * 2 + 1
    horner = ((2 - 0) * 2 - 3) * 2 + 1
    assert direct == 3
    assert horner == 3
    assert sp.simplify(sp.sympify("x**3 - 3*x + 1").subs("x", 2) - 3) == 0
