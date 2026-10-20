"""Algebra229 AS-B-22 factor x^2+1 over HTTP stays irreducible over Q."""
from pathlib import Path
import gzip
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"


def test_as_b22_source_row_present():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| AS-B-22 | N1 |" in text
    assert "Irreducible sobre ℚ y ℝ: debe quedar igual." in text


def test_as_b22_factor_x2_plus_1_http_unchanged():
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": "x^2+1"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    x = sp.symbols("x")
    got = sp.sympify(result["result_text"])
    assert sp.expand(got - (x**2 + 1)) == 0
    assert isinstance(got, sp.Add), result["result_text"]
