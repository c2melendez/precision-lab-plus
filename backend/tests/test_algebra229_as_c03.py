"""Algebra229 AS-C-03 simplify (x^2+3x+2)/(x^2-x-2): frozen row, exact result, excluded points."""
import gzip
from fractions import Fraction
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"
INPUT = "(x^2+3*x+2)/(x^2-x-2)"
EXPECTED = "(x+2)/(x-2)"
SAMPLES = (-5, -3, 0, 1, 3, 5)


def _compact(text: str) -> str:
    return "".join(text.split())


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


def test_as_c03_source_row_matches_all_frozen_contract_cells():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-C-03 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert len(cells) == 8, source_row
    assert cells[1:7] == [
        "AS-C-03",
        "N2",
        "`simplificar`",
        r"`\frac{x^{2}+3x+2}{x^{2}-x-2}`",
        r"`\frac{x + 2}{x - 2}`",
        "",
    ], source_row
    assert cells[7] == "", source_row


def test_as_c03_simplify_endpoint_returns_exact_result():
    result = _simplify(INPUT)
    # The engine prints powers as "**"; the frozen expectation writes them as "^".
    # Only the notation is normalized here, the mathematical expectation is unchanged.
    assert _compact(result["result_text"]).replace("**", "^") == _compact(EXPECTED), result


def test_as_c03_independent_arithmetic_matches_every_sample_outside_roots():
    for value in SAMPLES:
        expected = Fraction(value**2 + 3 * value + 2, value**2 - value - 2)
        assert expected == Fraction(value + 2, value - 2)
        result = _evaluate(f"(x^2+3*x+2)/(x^2-x-2) con x={value}")
        assert result["success"] is True, result
        assert Fraction(_compact(result["result_text"])) == expected, (value, result)


def test_as_c03_excluded_points_are_not_claimed_as_equivalent():
    for value in (2, -1):
        result = _evaluate(f"(x^2+3*x+2)/(x^2-x-2) con x={value}")
        assert result["success"] is False, result
        assert result["error_code"] == "DOMAIN_ERROR", result
