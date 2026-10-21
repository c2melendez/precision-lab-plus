"""Algebra229 AS-B-27 factor(1001) over HTTP returns 7*11*13."""
from pathlib import Path
import gzip
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"
INPUT = "factor(1001)"
EXPECTED = "7*11*13"


def test_as_b27_source_row_present():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| AS-B-27 | N2 |" in text
    assert "factorizar el entero " in text


def test_as_b27_factor_1001_http():
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": INPUT})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    assert result["result_text"].replace(" ", "") == EXPECTED
    got = sp.sympify(result["result_text"].replace("^", "**"))
    assert got == 1001
