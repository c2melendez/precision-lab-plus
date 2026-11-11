"""Trigonometría EC-H-04: cosh(x)=2 tiene dos raíces reales ±ln(2+sqrt(3))."""
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


def test_ec_h04_source_row_and_exact_two_roots_are_frozen():
    source = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    row = next((line for line in source.splitlines() if "| EC-H-04 |" in line), "")
    assert row
    cells = [cell.strip() for cell in row.split("|") if cell.strip()]
    assert len(cells) == 3, cells
    assert cells[0] == "EC-H-04", cells
    assert r"\cosh x=2" in cells[1]
    assert r"x=\pm\ln\left(2+\sqrt{3}\right)" in cells[2]


def test_ec_h04_http_solve_returns_exactly_two_real_logarithmic_roots():
    response = client.post(
        "/api/v1/solve",
        json={"equation": "cosh(x)=2", "variable": "x", "angle_unit": "rad"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["operation"] == "solve"
    assert body["result_type"] == "equation_solutions"
    assert body["result_data"] is not None

    actual = [sp.simplify(sp.sympify(item["text"])) for item in body["result_data"]]
    expected = sp.log(2 + sp.sqrt(3))
    assert len(actual) == 2, body
    assert any(sp.simplify(root - expected) == 0 for root in actual), actual
    assert any(sp.simplify(root + expected) == 0 for root in actual), actual
    assert all(root.is_real is True for root in actual), actual
    assert sp.simplify(actual[0] + actual[1]) == 0
    for root in actual:
        assert sp.simplify((sp.cosh(root) - 2).rewrite(sp.exp)) == 0
