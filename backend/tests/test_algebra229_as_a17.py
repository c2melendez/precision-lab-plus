"""Algebra229 AS-A-17 original expand (2x-y)^5 over HTTP."""
from pathlib import Path
import gzip
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"


def test_as_a17_source_row_present():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| AS-A-17 | N2 |" in text
    assert "32 x^{5} - 80 x^{4} y + 80 x^{3} y^{2} - 40 x^{2} y^{3} + 10 x y^{4} - y^{5}" in text


def test_as_a17_expand_fifth_power_http():
    with TestClient(app) as client:
        response = client.post("/api/v1/expand", json={"expression": "(2*x-y)^5"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    x, y = sp.symbols("x y")
    oracle = 32 * x**5 - 80 * x**4 * y + 80 * x**3 * y**2 - 40 * x**2 * y**3 + 10 * x * y**4 - y**5
    got = sp.sympify(result["result_text"])
    assert sp.expand(got - oracle) == 0
    assert "^5" not in result["result_text"].replace(" ", "")
