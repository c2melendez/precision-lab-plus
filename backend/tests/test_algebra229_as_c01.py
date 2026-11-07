"""Algebra229 AS-C-01 simplify (x^2-1)/(x-1): frozen row, endpoint, domain note."""
import gzip
from fractions import Fraction
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"
INPUT = "(x^2-1)/(x-1)"
EXPECTED = "x + 1"
SAMPLES = (-3, -2, 0, 2, 3, 5)


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


def test_as_c01_source_row_matches_all_frozen_contract_cells():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-C-01 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert len(cells) == 8, source_row
    assert cells[1:7] == [
        "AS-C-01",
        "N1",
        "`simplificar`",
        r"`\frac{x^{2}-1}{x-1}`",
        "`x + 1`",
        "Válido para `x\\neq1`.",
    ], source_row
    assert cells[7] == "", source_row


def test_as_c01_simplify_endpoint_returns_exact_result():
    result = _simplify(INPUT)
    assert result["result_text"] == EXPECTED, result


def test_as_c01_reports_the_domain_restriction_from_the_frozen_note():
    result = _simplify(INPUT)
    latex_conditions = {condition["latex"] for condition in result["domain_conditions"]}
    assert r"x \neq 1" in latex_conditions, result["domain_conditions"]


def test_as_c01_independent_arithmetic_matches_every_sample_outside_x_equals_1():
    for value in SAMPLES:
        expected = Fraction(value * value - 1, value - 1)
        assert expected == value + 1
        result = _evaluate(f"(x^2-1)/(x-1) con x={value}")
        assert result["success"] is True, result
        assert Fraction(result["result_text"]) == expected, (value, result)


def test_as_c01_excluded_point_is_not_claimed_as_equivalent():
    result = _evaluate("(x^2-1)/(x-1) con x=1")
    assert result["success"] is False, result
    assert result["error_code"] == "DOMAIN_ERROR", result
