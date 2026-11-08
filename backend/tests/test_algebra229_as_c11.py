"""Algebra229 AS-C-11 simplify continued fraction: frozen row, exact result, domain."""
import gzip
import re
from fractions import Fraction
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"
INPUT = "1/(1+1/(1+1/x))"
EXPECTED = "(x+1)/(2*x+1)"
SAMPLES = (-2, 1, 2, 3, 5)


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
        response = client.post("/api/v1/evaluate", json={"expression": expression})
    assert response.status_code == 200, response.text
    return response.json()


def _substitute_x(text: str, value: str) -> str:
    return re.sub(r"\bx\b", f"({value})", text)


def test_as_c11_source_row_matches_all_frozen_contract_cells():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-C-11 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert len(cells) == 8, source_row
    assert cells[1:7] == [
        "AS-C-11",
        "N3",
        "`simplificar`",
        r"`\frac{1}{1+\frac{1}{1+\frac{1}{x}}}`",
        r"`\frac{x + 1}{2 x + 1}`",
        "Fracción continua de tres niveles.",
    ], source_row
    assert cells[7] == "", source_row


def test_as_c11_simplify_endpoint_returns_one_combined_fraction():
    result = _simplify(INPUT)
    assert _canonical(result["result_text"]) == _canonical(EXPECTED), result
    difference = _simplify(f"({INPUT}) - ({EXPECTED})")
    assert Fraction(difference["result_text"]) == 0, (result, difference)


def test_as_c11_independent_arithmetic_matches_every_sample_outside_excluded_points():
    simplified = _simplify(INPUT)["result_text"]
    for value in SAMPLES:
        expected = Fraction(1, 1) / (1 + Fraction(1, 1) / (1 + Fraction(1, value)))
        assert expected == Fraction(value + 1, 2 * value + 1)
        direct = _evaluate(_substitute_x(INPUT, str(value)))
        assert Fraction(direct["result_text"]) == expected, (value, direct)
        from_result = _evaluate(_substitute_x(simplified, str(value)))
        assert Fraction(from_result["result_text"]) == expected, (value, simplified, from_result)


def test_as_c11_excluded_points_are_not_claimed_as_equivalent():
    for value in ("0", "-1", "-1/2"):
        result = _evaluate(_substitute_x(INPUT, value))
        assert result["success"] is False, result
        assert result["error_code"] == "DOMAIN_ERROR", result
