"""Trigonometría EC-H-01: sinh(x)=0 tiene la única solución real x=0."""
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


def test_ec_h01_source_row_and_exact_real_root_are_frozen():
    source = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    row = next((line for line in source.splitlines() if "| EC-H-01 |" in line), "")
    assert row
    assert r"\sinh x=0" in row
    assert "`x=0`" in row


def test_ec_h01_http_solve_returns_exactly_one_real_root():
    response = client.post(
        "/api/v1/solve",
        json={"equation": "sinh(x)=0", "variable": "x", "angle_unit": "rad"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["operation"] == "solve"
    assert body["result_type"] == "equation_solutions"
    assert body["result_data"] is not None

    actual = [sp.simplify(sp.sympify(item["text"])) for item in body["result_data"]]
    assert len(actual) == 1, body
    assert actual[0] == 0
    assert actual[0].is_real is True
    assert sp.simplify(sp.sinh(actual[0])) == 0
