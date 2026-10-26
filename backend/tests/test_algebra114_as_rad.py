"""Algebra114 AS-RAD-01..10: radical equations over R with extraneous roots rejected.

Every official solution must be returned, every candidate introduced by raising to a
power must be named and discarded, and each returned value must satisfy the
original equation with real semantics (principal even root, real odd root).
"""

import re
from pathlib import Path

import pytest
import sympy as sp
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.responses import ResultType
from app.services.solve_service import solve_equation

x = sp.Symbol("x")
S = sp.sympify

CASES = [
    ("AS-RAD-01", r"\(\sqrt{x}=-2\)", "sqrt(x)=-2", [], ["4"]),
    ("AS-RAD-02", r"\(\sqrt{x+3}=x+1\)", "sqrt(x+3)=x+1", ["1"], ["-2"]),
    ("AS-RAD-03", r"\(\sqrt{2x-1}=x-1\)", "sqrt(2*x-1)=x-1", ["2+sqrt(2)"], ["2-sqrt(2)"]),
    ("AS-RAD-04", r"\(\sqrt{x^{2}}=x-1\)", "sqrt(x**2)=x-1", [], ["1/2"]),
    ("AS-RAD-05", r"\(\sqrt{3-x}=x\)", "sqrt(3-x)=x", ["(-1+sqrt(13))/2"], ["(-1-sqrt(13))/2"]),
    ("AS-RAD-06", r"\(\sqrt[4]{x}=-1\)", "root(x,4)=-1", [], ["1"]),
    ("AS-RAD-07", r"\(\sqrt[3]{x-1}=x-1\)", "root(x-1,3)=x-1", ["0", "1", "2"], []),
    ("AS-RAD-08", r"\(\sqrt{x}+\sqrt{x-1}=1\)", "sqrt(x)+sqrt(x-1)=1", ["1"], []),
    ("AS-RAD-09", r"\(\sqrt{x-1}=x-3\)", "sqrt(x-1)=x-3", ["5"], ["2"]),
    ("AS-RAD-10", r"\(\sqrt{x}+\sqrt{x+3}=3\)", "sqrt(x)+sqrt(x+3)=3", ["1"], []),
]


def _real_residual(equation, value):
    lhs, rhs = (S(side) for side in equation.split("="))
    expr = (lhs - rhs).replace(
        lambda e: e.is_Pow and e.exp.is_Rational and e.exp.q % 2 == 1 and not e.exp.is_Integer,
        lambda e: sp.real_root(e.base, e.exp.q) ** e.exp.p,
    )
    return sp.simplify(expr.subs(x, value))


def _same(values, expected):
    return len(values) == len(expected) and all(
        any(sp.simplify(v - S(e)) == 0 for v in values) for e in expected
    )


@pytest.mark.parametrize("case_id,source_cell,equation,expected,extraneous", CASES)
def test_as_rad_source_rows(case_id, source_cell, equation, expected, extraneous):
    root = Path(__file__).resolve().parents[2]
    source = (root / "qa/certification/algebra114_source.md").read_text(encoding="utf-8")
    assert f"| {case_id} | " in source and f" | {source_cell} | " in source


@pytest.mark.parametrize("case_id,source_cell,equation,expected,extraneous", CASES)
def test_as_rad_service_and_http(case_id, source_cell, equation, expected, extraneous):
    result = solve_equation(equation, "x")
    values = [S(s.text) for s in result.solutions]
    assert _same(values, expected), (case_id, values)
    # Empty real sets keep the AS-PAR-06/07 radical contract (equation_solutions, no roots).
    assert result.result_type == ResultType.EQUATION_SOLUTIONS
    for value in values:
        assert _real_residual(equation, value) == 0, (case_id, value)
    assert result.has_detailed_steps is True
    text = " ".join(step.description for step in result.steps)
    rejected = [S(c) for c in re.findall(r"Candidato x = ([^:]+): [^;]*; se descarta", text)]
    assert _same(rejected, extraneous), (case_id, text)

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/solve", json={"equation": equation, "variable": "x", "angle_unit": "rad"}
        )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    assert payload["result_type"] == "equation_solutions"
    assert _same([S(i["text"]) for i in payload["result_data"] or []], expected)
