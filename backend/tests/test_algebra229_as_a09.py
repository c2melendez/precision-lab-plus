"""Algebra229 AS-A-09 original expand (x+1)(x+2)(x+3)(x+4) over HTTP."""
from pathlib import Path
import gzip
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"


def test_as_a09_source_row_present():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| AS-A-09 | N2 |" in text or "| AS-A-09 |" in text
    assert "(x+1)(x+2)(x+3)(x+4)" in text
    assert "x^{4} + 10 x^{3} + 35 x^{2} + 50 x + 24" in text


def test_as_a09_expand_four_linear_factors_http():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/expand",
            json={"expression": "(x+1)*(x+2)*(x+3)*(x+4)"},
        )
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    x = sp.symbols("x")
    oracle = x**4 + 10 * x**3 + 35 * x**2 + 50 * x + 24
    assert sp.simplify(sp.sympify(result["result_text"]) - oracle) == 0
