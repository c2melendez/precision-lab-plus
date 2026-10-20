"""Algebra229 AS-A-06 original expand (x+y+z)^2 over HTTP."""
from pathlib import Path
import gzip
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"


def test_as_a06_source_row_present():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| AS-A-06 | N2 |" in text or "| AS-A-06 |" in text
    assert "(x+y+z)" in text
    assert "x^{2} + 2 x y + 2 x z + y^{2} + 2 y z + z^{2}" in text


def test_as_a06_expand_trinomial_square_http():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/expand",
            json={"expression": "(x+y+z)**2"},
        )
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    x, y, z = sp.symbols("x y z")
    oracle = x**2 + 2 * x * y + 2 * x * z + y**2 + 2 * y * z + z**2
    assert sp.simplify(sp.sympify(result["result_text"]) - oracle) == 0
