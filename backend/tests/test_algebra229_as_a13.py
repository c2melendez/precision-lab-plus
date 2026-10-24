"""Algebra229 AS-A-13 original expand (x+h)^3-x^3 over HTTP."""
from pathlib import Path
import gzip
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"


def test_as_a13_source_row_present():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| AS-A-13 | N2 |" in text
    assert "(x+h)^{3}-x^{3}" in text
    assert "h^{3} + 3 h^{2} x + 3 h x^{2}" in text


def test_as_a13_expand_difference_of_cubes_http():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/expand",
            json={"expression": "(x+h)^3-x^3"},
        )
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    x, h = sp.symbols("x h")
    oracle = h**3 + 3 * h**2 * x + 3 * h * x**2
    assert sp.simplify(sp.sympify(result["result_text"]) - oracle) == 0
