"""Trigonometria EC-HI-02: arcosh x=0 tiene la raiz real exacta 1."""
from pathlib import Path
import gzip

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app
from app.services.solve_service import ResultType, solve_equation

SOURCE_GZ = (
    Path(__file__).resolve().parents[2]
    / "qa/certification/legacy_sources/ejercicios_trigonometria.md.gz"
)
client = TestClient(app)


def _source_row(identifier: str) -> list:
    source = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    line = next(
        (candidate for candidate in source.splitlines() if f"| {identifier} |" in candidate),
        "",
    )
    assert line, f"missing frozen source row {identifier}"
    cells = [cell.strip() for cell in line.split("|") if cell.strip()]
    assert len(cells) == 3, cells
    return cells


def test_ec_hi02_source_row_and_exact_root_are_frozen():
    cells = _source_row("EC-HI-02")
    assert cells[0] == "EC-HI-02", cells
    assert r"\operatorname{arcosh} x=0" in cells[1], cells
    assert r"x=1" in cells[2], cells


def test_ec_hi02_service_returns_exactly_one():
    result = solve_equation("acosh(x)=0", "x")
    assert result.result_type == ResultType.EQUATION_SOLUTIONS
    assert len(result.solutions) == 1, result.solutions
    root = sp.sympify(result.solutions[0].text.replace("^", "**"))
    assert sp.simplify(root - 1) == 0, root
    assert root.is_real is True, root


def test_ec_hi02_http_contract_returns_the_frozen_value():
    response = client.post(
        "/api/v1/solve",
        json={"equation": "acosh(x)=0", "variable": "x", "angle_unit": "rad"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["operation"] == "solve"
    assert body["result_type"] == "equation_solutions"
    assert body["result_data"] is not None
    assert len(body["result_data"]) == 1, body

    root = sp.sympify(body["result_data"][0]["text"].replace("^", "**"))
    assert sp.simplify(root - 1) == 0, root

    # Independent oracle: the source equation is satisfied by the returned root.
    assert sp.simplify(sp.acosh(root)) == 0, root
    # Real-domain solveset confirms exactly one real preimage of 0 under acosh (domain [1, ∞)).
    t = sp.Symbol("t", real=True)
    assert sp.solveset(sp.Eq(sp.acosh(t), 0), t, domain=sp.S.Reals) == sp.FiniteSet(1)
