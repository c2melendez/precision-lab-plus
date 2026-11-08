"""Algebra229 AS-C-08 simplify (x+1)/(x^2-1)-1/(x-1): frozen row, exact zero, domain."""
import gzip
from fractions import Fraction
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"
INPUT = "(x+1)/(x^2-1)-1/(x-1)"
SAMPLES = (-3, -2, 0, 2, 3, 5)


def _simplify(expression: str) -> dict:
    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": expression})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    return result


def _evaluate(expression: str) -> dict:
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
    assert response.status_code == 200, response.text
    return response.json()


def test_as_c08_source_row_matches_all_frozen_contract_cells():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-C-08 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert len(cells) == 8, source_row
    assert cells[1:7] == [
        "AS-C-08",
        "N2",
        "`simplificar`",
        r"`\frac{x+1}{x^{2}-1}-\frac{1}{x-1}`",
        "`0`",
        "",
    ], source_row
    assert cells[7] == "", source_row


def test_as_c08_simplify_endpoint_returns_exact_zero():
    result = _simplify(INPUT)
    assert result["result_text"].strip() == "0", result


def test_as_c08_independent_arithmetic_is_zero_at_every_sample_outside_x_equals_plus_minus_1():
    for value in SAMPLES:
        expected = Fraction(value + 1, value * value - 1) - Fraction(1, value - 1)
        assert expected == 0
        actual = _evaluate(f"({INPUT}) con x={value}")
        assert actual["success"] is True, actual
        assert Fraction(actual["result_text"]) == 0, (value, actual)


def test_as_c08_excluded_points_are_not_claimed_as_zero():
    for value in (1, -1):
        result = _evaluate(f"({INPUT}) con x={value}")
        assert result["success"] is False, result
        assert result["error_code"] == "DOMAIN_ERROR", result
