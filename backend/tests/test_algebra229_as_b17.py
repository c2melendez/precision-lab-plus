"""Algebra229 AS-B-17 original factor a^3+b^3 over HTTP."""
from pathlib import Path
import gzip
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"


def test_as_b17_source_row_present():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| AS-B-17 | N2 |" in text
    assert "\\left(a + b\\right) \\left(a^{2} - a b + b^{2}\\right)" in text


def test_as_b17_factor_a3_plus_b3_http():
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": "a^3+b^3"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    a, b = sp.symbols("a b")
    got = sp.sympify(result["result_text"])
    assert sp.expand(got - (a**3 + b**3)) == 0
    assert isinstance(got, sp.Mul), result["result_text"]
    assert len(got.args) == 2, result["result_text"]
