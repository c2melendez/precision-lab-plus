"""Trigonometría EC-I-05: atan(x)+atan(2x)=pi/4 tiene exactamente x=(sqrt(17)-3)/4."""
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


def test_ec_i05_source_row_and_exact_oracle_are_frozen():
    source = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| EC-I-05 |" in source
    assert r"\arctan x+\arctan(2x)=\frac{\pi}{4}" in source
    assert r"x=\frac{\sqrt{17}-3}{4}" in source


def test_ec_i05_http_solve_returns_exactly_one_root_verified_in_original_equation():
    response = client.post(
        "/api/v1/solve",
        json={"equation": "atan(x)+atan(2*x)=pi/4", "variable": "x", "angle_unit": "rad"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["operation"] == "solve"
    assert body["result_data"] is not None

    actual = [sp.simplify(sp.sympify(item["text"])) for item in body["result_data"]]
    assert len(actual) == 1
    assert sp.simplify(actual[0] - (sp.sqrt(17) - 3) / 4) == 0
    residual = sp.N(sp.atan(actual[0]) + sp.atan(2 * actual[0]) - sp.pi / 4, 30)
    assert abs(residual) < 1e-12
