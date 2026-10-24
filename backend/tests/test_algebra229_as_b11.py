"""Algebra229 AS-B-11 original factor ax+ay+bx+by over HTTP."""
from pathlib import Path
import gzip
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"


def test_as_b11_source_row_present():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| AS-B-11 | N2 |" in text
    assert "ax+ay+bx+by" in text
    assert "\\left(a + b\\right) \\left(x + y\\right)" in text


def test_as_b11_factor_grouping_http():
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": "a*x+a*y+b*x+b*y"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    a, b, x, y = sp.symbols("a b x y")
    got = sp.sympify(result["result_text"])
    assert sp.expand(got - (a * x + a * y + b * x + b * y)) == 0
    assert isinstance(got, sp.Mul), result["result_text"]
    assert sorted(map(str, got.args)) == sorted(map(str, [a + b, x + y])), result["result_text"]
