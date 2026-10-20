"""Algebra229 AS-B-15 original factor x^3-x^2-x+1 over HTTP."""
from pathlib import Path
import gzip
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"


def test_as_b15_source_row_present():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| AS-B-15 | N2 |" in text
    assert "\\left(x - 1\\right)^{2} \\left(x + 1\\right)" in text


def test_as_b15_factor_x3_x2_x_1_http():
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": "x^3-x^2-x+1"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    x = sp.symbols("x")
    got = sp.sympify(result["result_text"])
    assert sp.expand(got - (x**3 - x**2 - x + 1)) == 0
    assert isinstance(got, sp.Mul), result["result_text"]
    assert len(got.args) == 2, result["result_text"]
    assert sp.Pow(x - 1, 2) in got.args or sp.factor(got) == sp.factor(x**3 - x**2 - x + 1)
