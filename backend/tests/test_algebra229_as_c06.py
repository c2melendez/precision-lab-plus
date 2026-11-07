"""Algebra229 AS-C-06 simplify ((1/x)-(1/y))/(x-y): frozen row, canonical result, excluded points."""
import gzip
from fractions import Fraction
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"
INPUT = "((1/x)-(1/y))/(x-y)"
EXPECTED = "-1/(x*y)"
SAMPLES = ((1, 2), (-3, 2), (2, -5), (3, 4), (-4, -7))


def _canonical(text: str) -> str:
    # Whitespace and the "*" product sign are notation only.
    return "".join(text.split()).replace("*", "").replace("**", "^")


def _simplify(expression: str) -> dict:
    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": expression})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    assert result["operation"] == "simplify", result
    assert result["request_id"], result
    return result


def _evaluate(expression: str) -> dict:
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
    assert response.status_code == 200, response.text
    return response.json()


def test_as_c06_source_row_matches_all_frozen_contract_cells():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-C-06 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert len(cells) == 8, source_row
    assert cells[1:7] == [
        "AS-C-06",
        "N2",
        "`simplificar`",
        r"`\frac{\frac{1}{x}-\frac{1}{y}}{x-y}`",
        r"`- \frac{1}{x y}`",
        "",
    ], source_row
    assert cells[7] == "", source_row


def test_as_c06_simplify_endpoint_returns_canonical_result():
    result = _simplify(INPUT)
    assert _canonical(result["result_text"]) == _canonical(EXPECTED), result


def test_as_c06_independent_arithmetic_matches_every_sample_with_x_y_nonzero_and_x_neq_y():
    for x, y in SAMPLES:
        expected = Fraction(1, x) - Fraction(1, y)
        expected = expected / Fraction(x - y)
        assert expected == Fraction(-1, x * y)
        result = _evaluate(f"((1/({x}))-(1/({y})))/(({x})-({y}))")
        assert result["success"] is True, result
        assert Fraction(_canonical(result["result_text"])) == expected, (x, y, result)


def test_as_c06_excluded_points_are_not_claimed_as_equivalent():
    for expression in (
        "((1/(0))-(1/(2)))/((0)-(2))",
        "((1/(2))-(1/(0)))/((2)-(0))",
        "((1/(3))-(1/(3)))/((3)-(3))",
    ):
        result = _evaluate(expression)
        assert result["success"] is False, result
        assert result["error_code"] == "DOMAIN_ERROR", result
