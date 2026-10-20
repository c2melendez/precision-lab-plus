"""Algebra229 AS-A-14 original expand (sqrt(2)+sqrt(3))^2 over HTTP."""
from pathlib import Path
import gzip
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"


def test_as_a14_source_row_present():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| AS-A-14 | N2 |" in text
    assert "\\left(\\sqrt{2}+\\sqrt{3}\\right)^{2}" in text
    assert "2 \\sqrt{6} + 5" in text


def test_as_a14_expand_radical_square_http():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/expand",
            json={"expression": "(sqrt(2)+sqrt(3))^2"},
        )
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    oracle = 5 + 2 * sp.sqrt(6)
    # equivalencia_simbolica exacta: la diferencia se simplifica a 0 (sin muestreo numérico).
    assert sp.simplify(sp.sympify(result["result_text"]) - oracle) == 0
    # y el resultado no conserva el cuadrado sin expandir
    assert "**2" not in result["result_text"].replace(" ", "")
