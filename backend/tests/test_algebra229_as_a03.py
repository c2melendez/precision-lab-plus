"""Algebra229 AS-A-03 original expand (a+b)(a-b) over HTTP."""
from pathlib import Path
import gzip
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"


def test_as_a03_source_row_present():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| AS-A-03 | N1 |" in text or "| AS-A-03 |" in text
    assert "(a+b)(a-b)" in text
    assert "a^{2} - b^{2}" in text


def test_as_a03_expand_difference_of_squares_http():
    with TestClient(app) as client:
        response = client.post("/api/v1/expand", json={"expression": "(a+b)*(a-b)"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    a, b = sp.symbols("a b")
    assert sp.simplify(sp.sympify(result["result_text"]) - (a**2 - b**2)) == 0
