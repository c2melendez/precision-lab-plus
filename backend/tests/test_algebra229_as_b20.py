"""Algebra229 AS-B-20 factor x^4+x^2y^2+y^4 over HTTP."""
from pathlib import Path
import gzip
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"


def test_as_b20_source_row_present():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| AS-B-20 | N3 |" in text
    assert "\\left(x^{2} - x y + y^{2}\\right) \\left(x^{2} + x y + y^{2}\\right)" in text


def test_as_b20_factor_x4_x2y2_y4_http():
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": "x^4+x^2*y^2+y^4"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    x, y = sp.symbols("x y")
    got = sp.sympify(result["result_text"])
    assert sp.expand(got - (x**4 + x**2 * y**2 + y**4)) == 0
    assert isinstance(got, sp.Mul), result["result_text"]
    assert len(got.args) == 2, result["result_text"]
