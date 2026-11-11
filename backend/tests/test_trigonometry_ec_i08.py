"""Trigonometría EC-I-08: acsc(x)=pi/6 tiene exactamente x=2."""
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


def test_ec_i08_source_row_and_exact_oracle_are_frozen():
    source = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| EC-I-08 |" in source
    assert r"\operatorname{arccsc} x=\frac{\pi}{6}" in source
    assert "`x=2`" in source


def test_ec_i08_http_solve_returns_exactly_one_root_on_the_principal_branch():
    response = client.post(
        "/api/v1/solve",
        json={"equation": "acsc(x)=pi/6", "variable": "x", "angle_unit": "rad"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["operation"] == "solve"
    assert body["result_data"] is not None

    actual = [sp.simplify(sp.sympify(item["text"])) for item in body["result_data"]]
    assert len(actual) == 1
    assert sp.simplify(actual[0] - 2) == 0
    # Independent check of the principal branch: csc(pi/6)=2, so sin(pi/6)=1/x.
    residual = sp.N(sp.sin(sp.pi / 6) - 1 / actual[0], 30)
    assert abs(residual) < 1e-12
