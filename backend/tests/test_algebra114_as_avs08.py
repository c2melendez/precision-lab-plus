"""Algebra114 AS-AVS-08: abs(x-1)=x+1 solved by cases over R."""

from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.responses import ResultType
from app.services.solve_service import solve_equation

x = sp.Symbol("x")
EQUATION = "abs(x-1)=x+1"
EXPECTED = [sp.Integer(0)]


def test_as_avs_08_source_row():
    root = Path(__file__).resolve().parents[2]
    source = (root / "qa/certification/algebra114_source.md").read_text(encoding="utf-8")
    assert "| AS-AVS-08 | N3 | \\(|x-1|=x+1\\) | \\(x=0\\) |" in source


def test_as_avs_08_cases_service_and_http():
    lhs, rhs = (sp.sympify(side) for side in EQUATION.split("="))
    result = solve_equation(EQUATION, "x")
    assert result.result_type == ResultType.EQUATION_SOLUTIONS
    values = [sp.sympify(solution.text) for solution in result.solutions]
    assert values == EXPECTED
    assert all(sp.simplify((lhs - rhs).subs(x, value)) == 0 for value in values)
    assert result.has_detailed_steps is True
    assert "sin solución" in " ".join(step.description for step in result.steps)

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/solve", json={"equation": EQUATION, "variable": "x", "angle_unit": "rad"}
        )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    assert payload["result_type"] == "equation_solutions"
    assert [sp.sympify(item["text"]) for item in payload["result_data"]] == EXPECTED
