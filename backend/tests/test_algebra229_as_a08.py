"""Algebra229 AS-A-08 original expand (x-1)^5 over HTTP."""
from pathlib import Path
import gzip
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"


def test_as_a08_source_row_present():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| AS-A-08 | N2 |" in text or "| AS-A-08 |" in text
    assert "(x-1)" in text
    assert "x^{5} - 5 x^{4} + 10 x^{3} - 10 x^{2} + 5 x - 1" in text


def test_as_a08_expand_binomial_power_http():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/expand",
            json={"expression": "(x-1)**5"},
        )
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    x = sp.symbols("x")
    oracle = x**5 - 5 * x**4 + 10 * x**3 - 10 * x**2 + 5 * x - 1
    assert sp.simplify(sp.sympify(result["result_text"]) - oracle) == 0
