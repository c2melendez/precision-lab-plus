"""Algebra229 AS-C-07 simplify 1/(x-1)-1/(x+1): frozen row, equivalence, domain."""
import gzip
from fractions import Fraction
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"
INPUT = "1/(x-1)-1/(x+1)"
EXPECTED = "2/((x-1)*(x+1))"
SAMPLES = (-3, -2, 0, 2, 3, 5)


def _canonical(text: str) -> str:
    return text.replace("**", "^").replace(" ", "").replace("*", "")


def _simplify(expression: str) -> dict:
    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": expression})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    return result


def _evaluate(expression: str) -> dict:
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression.replace("**", "^")})
    assert response.status_code == 200, response.text
    return response.json()


def test_as_c07_source_row_matches_all_frozen_contract_cells():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-C-07 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert len(cells) == 8, source_row
    assert cells[1:7] == [
        "AS-C-07",
        "N2",
        "`simplificar`",
        r"`\frac{1}{x-1}-\frac{1}{x+1}`",
        r"`\frac{2}{\left(x - 1\right) \left(x + 1\right)}`",
        "",
    ], source_row
    assert cells[7] == "", source_row


def test_as_c07_endpoint_returns_a_simplified_equivalent_result():
    result = _simplify(INPUT)
    # The engine may keep the expanded denominator; equivalence is checked exactly, not textually.
    assert _canonical(result["result_text"]) != _canonical(INPUT), result
    difference = _simplify(f"({result['result_text']}) - ({EXPECTED})")
    assert Fraction(difference["result_text"]) == 0, (result, difference)


def test_as_c07_independent_arithmetic_matches_every_sample_outside_x_equals_plus_minus_1():
    result = _simplify(INPUT)["result_text"]
    for value in SAMPLES:
        expected = Fraction(2, value * value - 1)
        assert expected == Fraction(1, value - 1) - Fraction(1, value + 1)
        actual = _evaluate(f"({result}) con x={value}")
        assert actual["success"] is True, actual
        assert Fraction(actual["result_text"]) == expected, (value, result, actual)


def test_as_c07_excluded_points_are_not_claimed_as_equivalent():
    for value in (1, -1):
        result = _evaluate(f"1/(x-1)-1/(x+1) con x={value}")
        assert result["success"] is False, result
        assert result["error_code"] == "DOMAIN_ERROR", result
