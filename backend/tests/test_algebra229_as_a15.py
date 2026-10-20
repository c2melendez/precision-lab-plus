"""Algebra229 AS-A-15 original expand (x+1/x)^3 over HTTP."""
from pathlib import Path
import gzip
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"


def test_as_a15_source_row_present():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| AS-A-15 | N3 |" in text
    assert "\\left(x+\\frac{1}{x}\\right)^{3}" in text
    assert "x^{3} + 3 x + \\frac{3}{x} + \\frac{1}{x^{3}}" in text


def test_as_a15_expand_negative_exponents_http():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/expand",
            json={"expression": "(x+1/x)^3"},
        )
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    x = sp.symbols("x")
    oracle = x**3 + 3 * x + 3 / x + 1 / x**3
    got = sp.sympify(result["result_text"])
    assert sp.simplify(got - oracle) == 0
    # expandido de verdad: sin la potencia cúbica del binomio
    assert "**3)" not in result["result_text"].replace(" ", "")
    assert sp.expand(got) == sp.expand(oracle)
