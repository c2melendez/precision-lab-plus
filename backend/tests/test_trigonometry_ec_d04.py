"""Trigonometría EC-D-04: tres raíces exactas en [0, 2*pi)."""
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


def test_ec_d04_source_row_and_exact_oracle_are_frozen():
    source = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| EC-D-04 |" in source
    assert r"2\sin^{2}x-\sin x-1=0,\quad x\in[0,2\pi)" in source
    assert r"x=\frac{\pi}{2},\ \frac{7\pi}{6},\ \frac{11\pi}{6}" in source


def test_ec_d04_http_solve_returns_exact_three_roots_in_half_open_interval():
    response = client.post(
        "/api/v1/solve",
        json={"equation": "2*sin(x)^2-sin(x)-1=0", "variable": "x", "angle_unit": "rad"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["operation"] == "solve"
    assert body["result_data"] is not None

    actual = [sp.simplify(sp.sympify(item["text"])) for item in body["result_data"]]
    expected = {sp.pi / 2, 7 * sp.pi / 6, 11 * sp.pi / 6}
    assert len(actual) == 3
    assert {sp.simplify(value) for value in actual} == expected
    assert all(sp.simplify(2 * sp.sin(value)**2 - sp.sin(value) - 1) == 0 for value in actual)
    assert all(value >= 0 and value < 2 * sp.pi for value in actual)
