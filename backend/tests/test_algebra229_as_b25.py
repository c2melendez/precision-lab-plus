"""Algebra229 AS-B-25 factor x^2+1 sobre ℂ over HTTP returns (x-i)*(x+i)."""
from pathlib import Path
import gzip
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"
INPUT = "factor(x^2+1) sobre ℂ"
EXPECTED = "(x-i)*(x+i)"


def test_as_b25_source_row_present():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| AS-B-25 | N3 |" in text
    assert "Sobre ℂ se descompone." in text


def test_as_b25_factor_x2_plus_1_sobre_complejos_http():
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": INPUT})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    assert result["result_text"].replace(" ", "") == EXPECTED
    x = sp.symbols("x")
    got = sp.sympify(result["result_text"], locals={"i": sp.I})
    assert sp.expand(got - (x**2 + 1)) == 0


def test_as_b25_plain_x2_plus_1_is_not_factored_over_complex_by_default():
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": "x^2+1"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    assert result["result_text"].replace(" ", "") != EXPECTED
