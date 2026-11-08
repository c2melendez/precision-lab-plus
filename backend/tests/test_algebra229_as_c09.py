"""Algebra229 AS-C-09 simplify a/b+b/a: frozen row, combined fraction, domain."""
import gzip
import re
from fractions import Fraction
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"
INPUT = "a/b+b/a"
EXPECTED = "(a^2+b^2)/(a*b)"
SAMPLES = ((1, 2), (-3, 2), (2, -5), (3, 4), (-4, -7))


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


def _substitute(text: str, a: int, b: int) -> str:
    return re.sub(r"\b[ab]\b", lambda match: f"({a})" if match.group(0) == "a" else f"({b})", text)


def test_as_c09_source_row_matches_all_frozen_contract_cells():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    source_row = next(line.strip() for line in text.splitlines() if line.startswith("| AS-C-09 |"))
    cells = [cell.strip() for cell in source_row.split("|")]
    assert len(cells) == 8, source_row
    assert cells[1:7] == [
        "AS-C-09",
        "N2",
        "`simplificar`",
        r"`\frac{a}{b}+\frac{b}{a}`",
        r"`\frac{a^{2} + b^{2}}{a b}`",
        "",
    ], source_row
    assert cells[7] == "", source_row


def test_as_c09_simplify_endpoint_returns_one_combined_fraction():
    result = _simplify(INPUT)
    assert _canonical(result["result_text"]) == _canonical(EXPECTED), result
    difference = _simplify(f"({INPUT}) - ({EXPECTED})")
    assert Fraction(difference["result_text"]) == 0, (result, difference)


def test_as_c09_independent_arithmetic_matches_every_sample_with_a_b_nonzero():
    simplified = _simplify(INPUT)["result_text"]
    for a, b in SAMPLES:
        expected = Fraction(a, b) + Fraction(b, a)
        assert expected == Fraction(a * a + b * b, a * b)
        direct = _evaluate(_substitute(INPUT, a, b))
        assert Fraction(direct["result_text"]) == expected, (a, b, direct)
        from_result = _evaluate(_substitute(simplified, a, b))
        assert Fraction(from_result["result_text"]) == expected, (a, b, simplified, from_result)


def test_as_c09_excluded_points_are_not_claimed_as_equivalent():
    for a, b in ((0, 2), (2, 0), (0, 0)):
        result = _evaluate(_substitute(INPUT, a, b))
        assert result["success"] is False, result
        assert result["error_code"] == "DOMAIN_ERROR", result
