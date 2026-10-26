"""Algebra229 AS-A-07 original expand (2x-3)^4 over HTTP."""
from pathlib import Path
import gzip
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"


def test_as_a07_source_row_present():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| AS-A-07 | N2 |" in text or "| AS-A-07 |" in text
    assert "(2x-3)" in text
    assert "16 x^{4} - 96 x^{3} + 216 x^{2} - 216 x + 81" in text


def test_as_a07_expand_binomial_power_http():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/expand",
            json={"expression": "(2*x-3)**4"},
        )
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    x = sp.symbols("x")
    oracle = 16 * x**4 - 96 * x**3 + 216 * x**2 - 216 * x + 81
    assert sp.simplify(sp.sympify(result["result_text"]) - oracle) == 0
