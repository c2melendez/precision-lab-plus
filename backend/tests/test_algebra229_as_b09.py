"""Algebra229 AS-B-09 original factor 6x^2+5x-4 over HTTP."""
from pathlib import Path
import gzip
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"


def test_as_b09_source_row_present():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| AS-B-09 | N2 |" in text
    assert "\\left(2 x - 1\\right) \\left(3 x + 4\\right)" in text


def test_as_b09_factor_quadratic_http():
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": "6x^2+5x-4"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    x = sp.symbols("x")
    got = sp.sympify(result["result_text"])
    assert sp.expand(got - (6 * x**2 + 5 * x - 4)) == 0
    assert isinstance(got, sp.Mul), result["result_text"]
    assert len(got.args) == 2, result["result_text"]
