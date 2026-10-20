"""Algebra229 AS-A-16 original expand (1+i)^4 over HTTP."""
from pathlib import Path
import gzip
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"


def test_as_a16_source_row_present():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| AS-A-16 | N2 |" in text
    assert "(1+i)^{4}" in text


def test_as_a16_expand_imaginary_unit_http():
    with TestClient(app) as client:
        response = client.post("/api/v1/expand", json={"expression": "(1+i)^4"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    got = sp.sympify(result["result_text"], locals={"i": sp.I, "I": sp.I})
    assert sp.simplify(got - (-4)) == 0
    assert "^4" not in result["result_text"].replace(" ", "")
