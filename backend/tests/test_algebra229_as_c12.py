"""Algebra229 AS-C-12 simplify (x^2-y^2)/(x-y)^2: frozen row, exact result, excluded points."""
import gzip
from fractions import Fraction
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"
INPUT = "(x^2-y^2)/((x-y)^2)"
EXPECTED = "(x+y)/(x-y)"
SAMPLES = ((3, 1), (-2, 5), (0, 4), (7, -3), (1, -1))


def _canonical(text: str) -> str:
    # Whitespace and the "*" product sign are notation only; the expectation stays (x+y)/(x-y).
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


def test_as_c12_source_row_matches_all_frozen_contract_cells():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-C-12 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert len(cells) == 8, source_row
    assert cells[1:7] == [
        "AS-C-12",
        "N2",
        "`simplificar`",
        r"`\frac{x^{2}-y^{2}}{(x-y)^{2}}`",
        r"`\frac{x + y}{x - y}`",
        "",
    ], source_row
    assert cells[7] == "", source_row


def test_as_c12_simplify_endpoint_returns_exact_result():
    result = _simplify(INPUT)
    assert _canonical(result["result_text"]) == _canonical(EXPECTED), result


def test_as_c12_independent_arithmetic_matches_every_sample_with_x_not_equal_y():
    for x, y in SAMPLES:
        expected = Fraction(x * x - y * y, (x - y) ** 2)
        assert expected == Fraction(x + y, x - y)
        result = _evaluate(f"((x^2-y^2)/((x-y)^2)) con x={x}, y={y}")
        assert result["success"] is True, result
        assert Fraction(_canonical(result["result_text"])) == expected, (x, y, result)


def test_as_c12_excluded_points_are_not_claimed_as_equivalent():
    for value in (3, -2):
        result = _evaluate(f"((x^2-y^2)/((x-y)^2)) con x={value}, y={value}")
        assert result["success"] is False, result
        assert result["error_code"] == "DOMAIN_ERROR", result
