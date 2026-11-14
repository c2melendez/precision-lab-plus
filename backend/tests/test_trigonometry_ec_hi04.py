"""Trigonometria EC-HI-04: arcosh x=ln 2 tiene la raiz real exacta 5/4."""
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


def test_ec_hi04_source_row_and_exact_root_are_frozen():
    cells = _source_row("EC-HI-04")
    assert cells[0] == "EC-HI-04", cells
    assert r"\operatorname{arcosh} x=\ln 2" in cells[1], cells
    assert r"x=\frac{5}{4}" in cells[2], cells


def test_ec_hi04_service_returns_exactly_five_quarters():
    result = solve_equation("arcosh(x)=ln(2)", "x")
    assert result.result_type == ResultType.EQUATION_SOLUTIONS
    assert len(result.solutions) == 1, result.solutions
    assert result.solutions[0].text.replace(" ", "") == "5/4", result.solutions[0].text
    root = sp.sympify(result.solutions[0].text.replace("^", "**"))
    assert root == sp.Rational(5, 4), root
    assert root.is_real is True, root


def test_ec_hi04_http_contract_returns_the_frozen_value():
    response = client.post(
        "/api/v1/solve",
        json={"equation": "arcosh(x)=ln(2)", "variable": "x", "angle_unit": "rad"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["operation"] == "solve"
    assert body["result_type"] == "equation_solutions"
    assert body["result_data"] is not None
    assert len(body["result_data"]) == 1, body

    root = sp.sympify(body["result_data"][0]["text"].replace("^", "**"))
    assert root == sp.Rational(5, 4), root

    # Independent oracle: cosh(ln 2) = (2 + 1/2)/2 = 5/4 and 5/4 >= 1.
    assert sp.simplify(sp.cosh(sp.log(2)) - sp.Rational(5, 4)) == 0
    assert abs(sp.N(sp.acosh(sp.Rational(5, 4)), 30) - sp.log(2).evalf(30)) < sp.Float("1e-25")
    t = sp.Symbol("t", real=True)
    assert sp.solveset(sp.Eq(sp.acosh(t), sp.log(2)), t, domain=sp.S.Reals) == sp.FiniteSet(
        sp.cosh(sp.log(2))
    )
    assert sp.Rational(5, 4) >= 1


def test_ec_hi04_accepts_the_acosh_alias_and_the_reversed_equality():
    alias = solve_equation("acosh(x)=ln(2)", "x")
    assert [solution.text.replace(" ", "") for solution in alias.solutions] == ["5/4"]

    reversed_result = solve_equation("ln(2)=arcosh(x)", "x")
    assert [solution.text.replace(" ", "") for solution in reversed_result.solutions] == ["5/4"]
