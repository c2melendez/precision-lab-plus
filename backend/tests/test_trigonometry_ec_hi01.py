"""Trigonometria EC-HI-01: arsinh x=1 tiene la raiz real exacta sinh 1."""
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


def test_ec_hi01_source_row_and_exact_root_are_frozen():
    cells = _source_row("EC-HI-01")
    assert cells[0] == "EC-HI-01", cells
    assert r"\operatorname{arsinh} x=1" in cells[1], cells
    assert r"x=\sinh 1\approx 1.175201194" in cells[2], cells


def test_ec_hi01_service_returns_exactly_sinh_one():
    result = solve_equation("asinh(x)=1", "x")
    assert result.result_type == ResultType.EQUATION_SOLUTIONS
    assert len(result.solutions) == 1, result.solutions
    root = sp.sympify(result.solutions[0].text.replace("^", "**"))
    assert sp.simplify(root - sp.sinh(1)) == 0, root
    assert root.is_real is True, root


def test_ec_hi01_http_contract_returns_the_frozen_value():
    response = client.post(
        "/api/v1/solve",
        json={"equation": "asinh(x)=1", "variable": "x", "angle_unit": "rad"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["operation"] == "solve"
    assert body["result_type"] == "equation_solutions"
    assert body["result_data"] is not None
    assert len(body["result_data"]) == 1, body

    root = sp.sympify(body["result_data"][0]["text"].replace("^", "**"))
    assert sp.simplify(root - sp.sinh(1)) == 0, root
    assert abs(sp.N(root, 30) - sp.Float("1.175201194")) < sp.Float("1e-9"), root

    # Independent oracle: the source equation is satisfied by the returned root.
    assert sp.simplify(sp.asinh(root) - 1) == 0, root
    # Real-domain solveset confirms exactly one real preimage of 1 under asinh.
    t = sp.Symbol("t", real=True)
    assert sp.solveset(sp.Eq(sp.asinh(t), 1), t, domain=sp.S.Reals) == sp.FiniteSet(
        sp.sinh(1)
    )
