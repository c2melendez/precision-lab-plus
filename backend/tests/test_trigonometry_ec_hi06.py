"""Trigonometria EC-HI-06: artanh x=arsinh x tiene la raiz real exacta 0."""
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


def test_ec_hi06_source_row_and_exact_root_are_frozen():
    cells = _source_row("EC-HI-06")
    assert cells[0] == "EC-HI-06", cells
    assert r"\operatorname{artanh} x=\operatorname{arsinh} x" in cells[1], cells
    assert r"x=0" in cells[2], cells


def test_ec_hi06_service_returns_exactly_zero():
    result = solve_equation("artanh(x)=arsinh(x)", "x")
    assert result.result_type == ResultType.EQUATION_SOLUTIONS
    assert len(result.solutions) == 1, result.solutions
    assert result.solutions[0].text.replace(" ", "") == "0", result.solutions[0].text


def test_ec_hi06_http_contract_returns_the_frozen_value():
    response = client.post(
        "/api/v1/solve",
        json={"equation": "artanh(x)=arsinh(x)", "variable": "x", "angle_unit": "rad"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["operation"] == "solve"
    assert body["result_type"] == "equation_solutions"
    assert body["result_data"] is not None
    assert len(body["result_data"]) == 1, body
    assert sp.sympify(body["result_data"][0]["text"].replace("^", "**")) == 0

    # Independent oracle: atanh(0) = asinh(0) = 0 and atanh dominates asinh on (0,1).
    assert sp.atanh(sp.Integer(0)) == 0
    assert sp.asinh(sp.Integer(0)) == 0
    for probe in (sp.Rational(1, 10), sp.Rational(1, 4), sp.Rational(1, 2), sp.Rational(9, 10)):
        assert sp.atanh(probe) > sp.asinh(probe)
    t = sp.Symbol("t", real=True)
    # Independent oracle: sinh is injective, so atanh(t)=asinh(t) is equivalent
    # to sinh(atanh(t)) = t, i.e. t/sqrt(1-t^2) = t, which only holds at t = 0.
    assert sp.simplify(sp.sinh(sp.atanh(t)) - t / sp.sqrt(1 - t**2)) == 0
    assert sp.solve(sp.Eq(t / sp.sqrt(1 - t**2), t), t) == [0]
    assert sp.simplify(sp.atanh(0) - sp.asinh(0)) == 0


def test_ec_hi06_accepts_the_atanh_asinh_aliases_and_the_reversed_equality():
    alias = solve_equation("atanh(x)=asinh(x)", "x")
    assert [solution.text.replace(" ", "") for solution in alias.solutions] == ["0"]

    reversed_result = solve_equation("arsinh(x)=artanh(x)", "x")
    assert [solution.text.replace(" ", "") for solution in reversed_result.solutions] == ["0"]
