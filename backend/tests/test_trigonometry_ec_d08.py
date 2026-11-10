"""Trigonometría EC-D-08: sec(x)=-2 en [0, 2*pi)."""
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


def test_ec_d08_source_row_and_exact_oracle_are_frozen():
    source = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| EC-D-08 |" in source
    assert r"\sec x=-2,\quad x\in[0,2\pi)" in source
    assert r"x=\frac{2\pi}{3},\ \frac{4\pi}{3}" in source


def test_ec_d08_http_solve_returns_exact_two_roots_in_half_open_interval():
    response = client.post(
        "/api/v1/solve",
        json={"equation": "sec(x)=-2", "variable": "x", "angle_unit": "rad"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["operation"] == "solve"
    assert body["result_data"] is not None

    actual = [sp.simplify(sp.sympify(item["text"])) for item in body["result_data"]]
    expected = {2 * sp.pi / 3, 4 * sp.pi / 3}
    assert len(actual) == 2
    assert {sp.simplify(value) for value in actual} == expected
    assert all(sp.simplify(1 / sp.cos(value) + 2) == 0 for value in actual)
    assert all(value >= 0 and value < 2 * sp.pi for value in actual)
