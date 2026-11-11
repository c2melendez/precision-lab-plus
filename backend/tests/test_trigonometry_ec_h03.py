"""Trigonometría EC-H-03: sinh(x)=1 tiene la única solución real ln(1+sqrt(2))."""
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


def test_ec_h03_source_row_and_exact_logarithmic_root_are_frozen():
    source = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    row = next((line for line in source.splitlines() if "| EC-H-03 |" in line), "")
    assert row
    assert r"\sinh x=1" in row
    assert r"x=\ln\left(1+\sqrt{2}\right)" in row


def test_ec_h03_http_solve_returns_exactly_one_real_logarithmic_root():
    response = client.post(
        "/api/v1/solve",
        json={"equation": "sinh(x)=1", "variable": "x", "angle_unit": "rad"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["operation"] == "solve"
    assert body["result_type"] == "equation_solutions"
    assert body["result_data"] is not None

    actual = [sp.simplify(sp.sympify(item["text"])) for item in body["result_data"]]
    expected = sp.log(1 + sp.sqrt(2))
    assert len(actual) == 1, body
    assert sp.simplify(actual[0] - expected) == 0
    assert actual[0].is_real is True
    assert sp.simplify(sp.sinh(actual[0]).rewrite(sp.exp) - 1) == 0
