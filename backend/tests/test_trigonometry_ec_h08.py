"""Trigonometría EC-H-08: sech x=1/2 tiene las dos soluciones reales ±ln(2+sqrt(3))."""
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


def test_ec_h08_source_row_and_exact_real_roots_are_frozen():
    source = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    row = next((line for line in source.splitlines() if "| EC-H-08 |" in line), "")
    assert row
    cells = [cell.strip() for cell in row.split("|") if cell.strip()]
    assert len(cells) == 3, cells
    assert cells[0] == "EC-H-08", cells
    assert r"\operatorname{sech} x=\frac{1}{2}" in cells[1]
    assert r"x=\pm\ln\left(2+\sqrt{3}\right)" in cells[2]


def test_ec_h08_http_solve_returns_exactly_two_real_logarithmic_roots():
    response = client.post(
        "/api/v1/solve",
        json={"equation": "sech(x)=1/2", "variable": "x", "angle_unit": "rad"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["operation"] == "solve"
    assert body["result_type"] == "equation_solutions"
    assert body["result_data"] is not None

    actual = [sp.simplify(sp.sympify(item["text"])) for item in body["result_data"]]
    assert len(actual) == 2, body
    expected = sp.log(2 + sp.sqrt(3))
    # log(2-sqrt(3)) and -log(2+sqrt(3)) denote the same real number, so compare
    # exponentials: exp(root) must be exp(+expected) or exp(-expected) exactly.
    plus_exps = [sp.simplify(sp.exp(root) - sp.exp(expected)) for root in actual]
    minus_exps = [sp.simplify(sp.exp(root) - sp.exp(-expected)) for root in actual]
    assert sum(check == 0 for check in plus_exps) == 1, actual
    assert sum(check == 0 for check in minus_exps) == 1, actual
    for root in actual:
        assert root.is_real is True, root
        # Original equation sech(x)=1/2, checked numerically and independently.
        assert abs(sp.N(sp.sech(root), 50) - sp.Rational(1, 2)) < sp.Float("1e-40"), root

    # Independent real-domain oracle: cosh(x)=2 has exactly ±acosh(2), and
    # acosh(2) is numerically the source closed form ln(2+sqrt(3)).
    t = sp.Symbol("t")
    assert sp.solveset(sp.cosh(t) - 2, t, domain=sp.S.Reals) == sp.FiniteSet(
        -sp.acosh(2), sp.acosh(2)
    )
    assert abs(sp.N(sp.acosh(2), 50) - sp.N(expected, 50)) < sp.Float("1e-40")
