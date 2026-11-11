"""Trigonometría EC-I-03: atan(x)=pi/4 tiene exactamente x=1."""
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


def test_ec_i03_source_row_and_exact_oracle_are_frozen():
    source = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| EC-I-03 |" in source
    assert r"\arctan x=\frac{\pi}{4}" in source
    assert "| x=1 |" in source or "`x=1`" in source


def test_ec_i03_http_solve_returns_exactly_one_root_verified_in_original_equation():
    response = client.post(
        "/api/v1/solve",
        json={"equation": "atan(x)=pi/4", "variable": "x", "angle_unit": "rad"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["operation"] == "solve"
    assert body["result_data"] is not None

    actual = [sp.simplify(sp.sympify(item["text"])) for item in body["result_data"]]
    assert len(actual) == 1
    assert actual[0] == sp.Integer(1)
    assert sp.simplify(sp.atan(actual[0]) - sp.pi / 4) == 0
