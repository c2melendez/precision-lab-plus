"""Cross-multiplying tangent addition must not introduce other atan branches."""
import os

os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")

import pytest
import sympy as sp

from app.services import parsing, solve_service

ROOT = (sp.sqrt(17)-3)/4


@pytest.mark.parametrize("equation,expected", [
    ("atan(x)+atan(2*x)=pi/4", [ROOT]),
    ("pi/4=atan(x)+atan(2*x)", [ROOT]),
    ("atan(2*x)+atan(x)=pi/4", [ROOT]),
    ("atan(x)+atan(2*x)=-pi/4", [-ROOT]),
    ("atan(x)+atan(2*x)=0", [0]),
    ("atan(x+1)+atan(2*x+2)=pi/4", [ROOT-1]),
])
def test_affine_atan_sum_service(equation, expected):
    result = solve_service.solve_equation(equation, "x", domain="real")
    actual = [sp.sympify(solution.text) for solution in result.solutions]
    assert len(actual) == len(expected)
    assert all(sp.simplify(a-b) == 0 for a, b in zip(actual, expected))
    assert result.input_eq == parsing.parse_expression_tree(equation, allow_equation=True)
    assert result.steps == []
    assert result.has_detailed_steps is False
    for value in actual:
        difference = result.input_eq.lhs-result.input_eq.rhs
        assert abs(float(sp.N(difference.subs(sp.Symbol("x"), value), 30))) < 1e-25


def test_atan_sum_rejects_negative_extraneous_branch_service():
    result = solve_service.solve_equation("atan(x)+atan(2*x)=pi/4", "x", domain="real")
    negative_root = -(sp.sqrt(17)+3)/4
    assert all(sp.simplify(sp.sympify(s.text)-negative_root) != 0 for s in result.solutions)
    assert sp.simplify(1-2*negative_root**2).is_negative is True


@pytest.mark.parametrize("lower,upper,left_closed,expected", [
    ("0", "1", True, [ROOT]),
    ("-2", "0", True, []),
    ("(sqrt(17)-3)/4", "1", False, []),
    ("(sqrt(17)-3)/4", "1", True, [ROOT]),
])
def test_atan_sum_requested_interval_service(lower, upper, left_closed, expected):
    result = solve_service.solve_equation(
        "atan(x)+atan(2*x)=pi/4", "x", domain="real",
        domain_lower=lower, domain_upper=upper, domain_lower_inclusive=left_closed,
    )
    actual = [sp.sympify(s.text) for s in result.solutions]
    assert len(actual) == len(expected)
    assert all(sp.simplify(a-b) == 0 for a, b in zip(actual, expected))


def test_atan_sum_unknown_branch_scope_is_declined_service():
    x = sp.Symbol("x")
    for equation in [sp.Eq(sp.atan(x)+sp.atan(2*x), sp.pi/2),
                     sp.Eq(sp.atan(x**2)+sp.atan(x), sp.pi/4)]:
        assert solve_service._real_affine_atan_sum(equation, x) is None


def test_atan_sum_roots_are_not_degree_converted_service():
    result = solve_service.solve_equation("atan(x)+atan(2*x)=pi/4", "x", domain="real", angle_unit="deg")
    assert len(result.solutions) == 1
    assert sp.simplify(sp.sympify(result.solutions[0].text)-ROOT) == 0


def test_atan_sum_api_exact_root():
    from fastapi.testclient import TestClient
    from app.main import app

    body = TestClient(app).post("/api/v1/solve", json={
        "equation": "atan(x)+atan(2*x)=pi/4", "variable": "x", "domain": "real",
    }).json()
    assert body["success"] is True, body
    assert len(body["result_data"]) == 1
    assert sp.simplify(sp.sympify(body["result_data"][0]["text"])-ROOT) == 0
