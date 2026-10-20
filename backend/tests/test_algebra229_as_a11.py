"""Algebra229 AS-A-11 original expand (a+b+c)^3 over HTTP."""
from pathlib import Path
import gzip
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/matriz_algebra_simbolica.md.gz"


def test_as_a11_source_row_present():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    # Verified against source fixture: AS-A-11 is level N2 (not N3).
    assert "| AS-A-11 | N2 |" in text
    assert "(a+b+c)^{3}" in text
    assert "a^{3} + 3 a^{2} b + 3 a^{2} c + 3 a b^{2} + 6 a b c + 3 a c^{2} + b^{3} + 3 b^{2} c + 3 b c^{2} + c^{3}" in text


def test_as_a11_expand_trinomial_multinomial_cube_http():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/expand",
            json={"expression": "(a+b+c)^3"},
        )
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    a, b, c = sp.symbols("a b c")
    oracle = (
        a**3 + 3 * a**2 * b + 3 * a**2 * c + 3 * a * b**2 + 6 * a * b * c
        + 3 * a * c**2 + b**3 + 3 * b**2 * c + 3 * b * c**2 + c**3
    )
    assert sp.simplify(sp.sympify(result["result_text"]) - oracle) == 0
