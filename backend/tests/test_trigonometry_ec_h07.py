"""Trigonometría EC-H-07: sinh(2x)=sinh x tiene la única solución real 0."""
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


def test_ec_h07_source_row_and_exact_real_root_are_frozen():
    source = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    row = next((line for line in source.splitlines() if "| EC-H-07 |" in line), "")
    assert row
    cells = [cell.strip() for cell in row.split("|") if cell.strip()]
    assert len(cells) == 3, cells
    assert cells[0] == "EC-H-07", cells
    assert r"\sinh(2x)=\sinh x" in cells[1]
    assert "x=0" in cells[2]


def test_ec_h07_http_solve_returns_exactly_one_real_zero_root():
    response = client.post(
        "/api/v1/solve",
        json={"equation": "sinh(2*x)=sinh(x)", "variable": "x", "angle_unit": "rad"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["operation"] == "solve"
    assert body["result_type"] == "equation_solutions"
    assert body["result_data"] is not None

    actual = [sp.simplify(sp.sympify(item["text"])) for item in body["result_data"]]
    assert len(actual) == 1, body
    assert sp.simplify(actual[0]) == 0
    assert actual[0].is_real is True
    assert sp.simplify(sp.sinh(2 * actual[0]) - sp.sinh(actual[0])) == 0

    # Independent uniqueness oracle over the real domain:
    # sinh(2x)-sinh(x)=sinh(x)*(2*cosh(x)-1) and 2*cosh(x)-1>0 for all real x,
    # so only sinh(x)=0 remains. solveset enforces the domain (solve does not).
    t = sp.Symbol("t")
    difference = sp.sinh(2 * t) - sp.sinh(t)
    assert sp.simplify(difference - sp.sinh(t) * (2 * sp.cosh(t) - 1)) == 0
    assert sp.solveset(difference, t, domain=sp.S.Reals) == sp.FiniteSet(0)
