"""Algebra229 AS-B-28 factor(4294967297) over HTTP returns 641*6700417."""
from pathlib import Path
import gzip
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"
INPUT = "factor(4294967297)"
EXPECTED = "641*6700417"


def test_as_b28_source_row_present():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| AS-B-28 | N3 |" in text
    assert "factorizar el entero " in text


def test_as_b28_factor_4294967297_http():
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": INPUT})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    assert result["result_text"].replace(" ", "") == EXPECTED
    got = sp.sympify(result["result_text"].replace("^", "**"))
    assert got == 4294967297
