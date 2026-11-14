"""Trigonometria EC-HI-07: arcosh x=arsinh x no tiene solucion real."""
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


def test_ec_hi07_source_row_and_empty_result_are_frozen():
    cells = _source_row("EC-HI-07")
    assert cells[0] == "EC-HI-07", cells
    assert r"\operatorname{arcosh} x=\operatorname{arsinh} x" in cells[1], cells
    assert "sin soluci" in cells[2].lower(), cells


def test_ec_hi07_service_reports_a_contradiction():
    result = solve_equation("arcosh(x)=arsinh(x)", "x")
    assert result.result_type == ResultType.CONTRADICTION, result.result_type
    assert result.solutions == [], result.solutions


def test_ec_hi07_http_contract_returns_the_frozen_empty_set():
    response = client.post(
        "/api/v1/solve",
        json={"equation": "arcosh(x)=arsinh(x)", "variable": "x", "angle_unit": "rad"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["operation"] == "solve"
    assert body["result_type"] == "contradiction"
    assert not body["result_data"], body


def test_ec_hi07_accepts_the_acosh_asinh_aliases_and_confirms_with_an_oracle():
    alias = solve_equation("acosh(x)=asinh(x)", "x")
    assert alias.result_type == ResultType.CONTRADICTION
    reversed_result = solve_equation("arsinh(x)=arcosh(x)", "x")
    assert reversed_result.result_type == ResultType.CONTRADICTION

    # Independent oracle: cosh(x) - sinh(x) = e^{-x} > 0, so cosh > sinh and,
    # inverting on the shared domain v >= 1, acosh(v) < asinh(v).
    t = sp.Symbol("t", real=True)
    assert sp.simplify(sp.cosh(t) - sp.sinh(t)) == sp.exp(-t)
    for probe in (1, sp.Rational(3, 2), 2, 5, 10):
        assert sp.acosh(probe) < sp.asinh(probe)
    # Exact reason: cosh is injective and increasing on [0, inf) and
    # cosh(asinh(t)) = sqrt(t^2+1), so equality would need t = sqrt(t^2+1),
    # i.e. t^2 = t^2+1.
    assert sp.simplify(sp.cosh(sp.asinh(t)) - sp.sqrt(t**2 + 1)) == 0
    assert sp.simplify(sp.sqrt(t**2 + 1) ** 2 - t**2) == 1
