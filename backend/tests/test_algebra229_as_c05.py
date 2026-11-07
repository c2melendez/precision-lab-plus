"""Algebra229 AS-C-05 simplify 1/x+1/y: frozen row, canonical common-denominator result, excluded points."""
import gzip
from fractions import Fraction
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"
INPUT = "1/x+1/y"
EXPECTED = "(x+y)/(xy)"
SAMPLES = ((1, 2), (-3, 2), (2, -5), (3, 3), (-4, -7))


def _canonical(text: str) -> str:
    # Whitespace and the "*" product sign are notation only; the expectation stays (x+y)/(xy).
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


def test_as_c05_source_row_matches_all_frozen_contract_cells():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-C-05 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert len(cells) == 8, source_row
    assert cells[1:7] == [
        "AS-C-05",
        "N1",
        "`simplificar`",
        r"`\frac{1}{x}+\frac{1}{y}`",
        r"`\frac{x + y}{x y}`",
        "Suma de fracciones con denominador común.",
    ], source_row
    assert cells[7] == "", source_row


def test_as_c05_simplify_endpoint_returns_canonical_result():
    result = _simplify(INPUT)
    assert _canonical(result["result_text"]) == _canonical(EXPECTED), result


def test_as_c05_independent_arithmetic_matches_every_sample_with_x_y_nonzero():
    for x, y in SAMPLES:
        expected = Fraction(x + y, x * y)
        assert expected == Fraction(1, x) + Fraction(1, y)
        result = _evaluate(f"1/({x})+1/({y})")
        assert result["success"] is True, result
        assert Fraction(_canonical(result["result_text"])) == expected, (x, y, result)


def test_as_c05_excluded_points_are_not_claimed_as_equivalent():
    for expression in ("1/(0)+1/(2)", "1/(2)+1/(0)"):
        result = _evaluate(expression)
        assert result["success"] is False, result
        assert result["error_code"] == "DOMAIN_ERROR", result
