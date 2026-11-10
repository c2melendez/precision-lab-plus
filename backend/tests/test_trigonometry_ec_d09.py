"""Trigonometría EC-D-09: cot(x)=1 en [0, 2*pi)."""
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


def test_ec_d09_source_row_and_exact_oracle_are_frozen():
    source = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| EC-D-09 |" in source
    assert r"\cot x=1,\quad x\in[0,2\pi)" in source
    assert r"x=\frac{\pi}{4},\ \frac{5\pi}{4}" in source


def test_ec_d09_http_solve_returns_exact_two_roots_in_half_open_interval():
    response = client.post(
        "/api/v1/solve",
        json={"equation": "cot(x)=1", "variable": "x", "angle_unit": "rad"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["operation"] == "solve"
    assert body["result_data"] is not None

    actual = [sp.simplify(sp.sympify(item["text"])) for item in body["result_data"]]
    expected = {sp.pi / 4, 5 * sp.pi / 4}
    assert len(actual) == 2
    assert {sp.simplify(value) for value in actual} == expected
    assert all(sp.simplify(sp.cos(value) / sp.sin(value) - 1) == 0 for value in actual)
    assert all(value >= 0 and value < 2 * sp.pi for value in actual)
