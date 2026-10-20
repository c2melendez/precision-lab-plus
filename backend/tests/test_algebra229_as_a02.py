"""Algebra229 AS-A-02 original expand (x-y)^3 over HTTP."""
from pathlib import Path
import gzip
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"


def test_as_a02_source_row_present():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| AS-A-02 | N1 |" in text or "| AS-A-02 |" in text
    assert "(x-y)^{3}" in text


def test_as_a02_expand_cubic_difference_http():
    with TestClient(app) as client:
        response = client.post("/api/v1/expand", json={"expression": "(x-y)**3"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    x, y = sp.symbols("x y")
    oracle = x**3 - 3 * x**2 * y + 3 * x * y**2 - y**3
    assert sp.simplify(sp.sympify(result["result_text"]) - oracle) == 0
