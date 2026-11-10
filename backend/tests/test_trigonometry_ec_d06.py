"""Trigonometría EC-D-06: sin(2*x)=cos(x) en [0, 2*pi)."""
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


def test_ec_d06_source_row_and_exact_oracle_are_frozen():
    source = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| EC-D-06 |" in source
    assert r"\sin 2x=\cos x,\quad x\in[0,2\pi)" in source
    assert r"x=\frac{\pi}{6},\ \frac{\pi}{2},\ \frac{5\pi}{6},\ \frac{3\pi}{2}" in source


def test_ec_d06_http_solve_returns_exact_four_roots_in_half_open_interval():
    response = client.post(
        "/api/v1/solve",
        json={"equation": "sin(2*x)=cos(x)", "variable": "x", "angle_unit": "rad"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["operation"] == "solve"
    assert body["result_data"] is not None

    actual = [sp.simplify(sp.sympify(item["text"])) for item in body["result_data"]]
    expected = {
        sp.pi / 6,
        sp.pi / 2,
        5 * sp.pi / 6,
        3 * sp.pi / 2,
    }
    assert len(actual) == 4
    assert {sp.simplify(value) for value in actual} == expected
    assert all(sp.simplify(sp.sin(2 * value) - sp.cos(value)) == 0 for value in actual)
    assert all(value >= 0 and value < 2 * sp.pi for value in actual)
