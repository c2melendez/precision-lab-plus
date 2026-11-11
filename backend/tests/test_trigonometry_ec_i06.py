"""Trigonometría EC-I-06: acot(x)=2*pi/3 tiene exactamente x=-sqrt(3)/3."""
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


def test_ec_i06_source_row_and_exact_oracle_are_frozen():
    source = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| EC-I-06 |" in source
    assert r"\operatorname{arccot} x=\frac{2\pi}{3}" in source
    assert r"x=-\frac{\sqrt{3}}{3}" in source


def test_ec_i06_http_solve_returns_exactly_one_root_on_the_principal_branch():
    response = client.post(
        "/api/v1/solve",
        json={"equation": "acot(x)=2*pi/3", "variable": "x", "angle_unit": "rad"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["operation"] == "solve"
    assert body["result_data"] is not None

    actual = [sp.simplify(sp.sympify(item["text"])) for item in body["result_data"]]
    assert len(actual) == 1
    assert sp.simplify(actual[0] - (-sp.sqrt(3) / 3)) == 0
    residual = sp.N(sp.acot(actual[0]) - 2 * sp.pi / 3, 30)
    assert abs(residual) < 1e-12
