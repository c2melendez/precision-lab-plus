"""Trigonometría EC-D-05: sin(x)+cos(x)=1 en [0, 2*pi)."""
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


def test_ec_d05_source_row_and_exact_oracle_are_frozen():
    source = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| EC-D-05 |" in source
    assert r"\sin x+\cos x=1,\quad x\in[0,2\pi)" in source
    assert r"x=0,\ \frac{\pi}{2}" in source


def test_ec_d05_http_solve_returns_exact_two_roots_in_half_open_interval():
    response = client.post(
        "/api/v1/solve",
        json={"equation": "sin(x)+cos(x)=1", "variable": "x", "angle_unit": "rad"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["operation"] == "solve"
    assert body["result_data"] is not None

    actual = [sp.simplify(sp.sympify(item["text"])) for item in body["result_data"]]
    expected = {sp.Integer(0), sp.pi / 2}
    assert len(actual) == 2
    assert {sp.simplify(value) for value in actual} == expected
    assert all(sp.simplify(sp.sin(value) + sp.cos(value) - 1) == 0 for value in actual)
    assert all(value >= 0 and value < 2 * sp.pi for value in actual)
