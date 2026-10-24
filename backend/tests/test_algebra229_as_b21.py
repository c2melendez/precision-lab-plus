"""Algebra229 AS-B-21 factor (x^2+1)^2-4x^2 over HTTP."""
from pathlib import Path
import gzip
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"


def test_as_b21_source_row_present():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| AS-B-21 | N3 |" in text
    assert "\\left(x - 1\\right)^{2} \\left(x + 1\\right)^{2}" in text


def test_as_b21_factor_difference_of_squares_http():
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": "(x^2+1)^2-4*x^2"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    x = sp.symbols("x")
    got = sp.sympify(result["result_text"])
    assert sp.expand(got - ((x**2 + 1) ** 2 - 4 * x**2)) == 0
    assert sp.expand(got - (x - 1) ** 2 * (x + 1) ** 2) == 0
    assert isinstance(got, sp.Mul), result["result_text"]
