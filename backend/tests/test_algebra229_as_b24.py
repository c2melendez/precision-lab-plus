"""Algebra229 AS-B-24 factor x^2-2 sobre ℝ over HTTP returns (x-sqrt(2))*(x+sqrt(2))."""
from pathlib import Path
import gzip
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"
INPUT = "factor(x^2-2) sobre ℝ"
EXPECTED = "(x-sqrt(2))*(x+sqrt(2))"


def test_as_b24_source_row_present():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| AS-B-24 | N3 |" in text
    assert "Con raíces permitidas" in text


def test_as_b24_factor_x2_minus_2_sobre_reales_http():
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": INPUT})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    assert result["result_text"].replace(" ", "") == EXPECTED
    x = sp.symbols("x")
    got = sp.sympify(result["result_text"])
    assert sp.expand(got - (x**2 - 2)) == 0
