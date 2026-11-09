"""Trigonometría EC-D-01: sin(x)=1/2 en [0, 2*pi), vía POST /solve."""
from pathlib import Path
import gzip

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app

SOURCE_GZ = (
    Path(__file__).resolve().parents[2]
    / "qa/certification/legacy_sources/ejercicios_trigonometria.md.gz"
)
client = TestClient(app)


def test_ec_d01_source_row_and_exact_oracle_are_frozen():
    source = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| EC-D-01 |" in source
    assert r"\sin x=\frac{1}{2}" in source
    assert r"\frac{\pi}{6}" in source
    assert r"\frac{5\pi}{6}" in source


def test_ec_d01_http_solve_returns_both_exact_roots_in_interval():
    response = client.post(
        "/api/v1/solve",
        json={"equation": "sin(x)-1/2=0", "variable": "x", "angle_unit": "rad"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["operation"] == "solve"
    assert body["result_data"] is not None

    actual = [sp.sympify(item["text"]) for item in body["result_data"]]
    expected = {sp.pi / 6, 5 * sp.pi / 6}
    assert len(actual) == 2
    assert {sp.simplify(value) for value in actual} == expected
    assert all(sp.simplify(sp.sin(value) - sp.Rational(1, 2)) == 0 for value in actual)
    assert all(value >= 0 and value < 2 * sp.pi for value in actual)
