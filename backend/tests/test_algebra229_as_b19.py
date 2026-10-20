"""Algebra229 AS-B-19 factor common multivariable factor x^2y-xy^2 over HTTP."""
from pathlib import Path
import gzip
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"


def test_as_b19_source_row_present():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| AS-B-19 | N2 |" in text
    assert "x y \\left(x - y\\right)" in text


def test_as_b19_factor_common_multivariable_http():
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": "x^2*y-x*y^2"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    x, y = sp.symbols("x y")
    got = sp.sympify(result["result_text"])
    assert sp.expand(got - (x**2 * y - x * y**2)) == 0
    assert isinstance(got, sp.Mul), result["result_text"]
    assert len(got.args) == 3, result["result_text"]
