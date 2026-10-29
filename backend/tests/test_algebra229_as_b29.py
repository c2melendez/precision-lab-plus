"""Algebra229 AS-B-29 factor(123456789) over HTTP returns 3^2*3607*3803."""
from pathlib import Path
import gzip
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"
INPUT = "factor(123456789)"
EXPECTED = "3^2*3607*3803"


def test_as_b29_source_row_present():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| AS-B-29 | N2 |" in text
    assert "factorizar el entero " in text


def test_as_b29_factor_123456789_http():
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": INPUT})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    assert result["result_text"].replace(" ", "") == EXPECTED
    got = sp.sympify(result["result_text"].replace("^", "**"))
    assert got == 123456789
