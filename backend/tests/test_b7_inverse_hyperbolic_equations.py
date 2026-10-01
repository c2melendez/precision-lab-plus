"""Exact same-argument identities on real principal inverse branches."""
import os

os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")

import pytest
import sympy as sp

from app.services import parsing, solve_service


@pytest.mark.parametrize("equation,expected", [
    ("atanh(x)=asinh(x)", [0]),
    ("asinh(x)=atanh(x)", [0]),
    ("acosh(x)=asinh(x)", []),
    ("asinh(x)=acosh(x)", []),
    ("atanh(2*x-3)=asinh(2*x-3)", [sp.Rational(3, 2)]),
    ("asinh(x^2-1)=atanh(x^2-1)", [-1, 1]),
    ("atanh(x^2+1)=asinh(x^2+1)", []),
    ("acosh(2*x-3)=asinh(2*x-3)", []),
])
def test_same_argument_inverse_hyperbolic_service(equation, expected):
    result = solve_service.solve_equation(equation, "x", domain="real")
    assert {sp.sympify(s.text) for s in result.solutions} == set(expected)
    assert result.input_eq == parsing.parse_expression_tree(equation, allow_equation=True)
    assert result.has_detailed_steps is False
    assert result.steps == []
    for solution in result.solutions:
        value = sp.sympify(solution.text)
        assert sp.simplify(result.input_eq.lhs.subs(sp.Symbol("x"), value)
                           - result.input_eq.rhs.subs(sp.Symbol("x"), value)) == 0


@pytest.mark.parametrize("lower,upper,left_closed,right_closed,expected", [
    ("-1", "1", False, False, [0]),
    ("0", "1", False, True, []),
    ("0", "1", True, True, [0]),
    ("-1", "0", True, False, []),
    ("1", "2", True, True, []),
])
def test_inverse_hyperbolic_requested_domain_service(lower, upper, left_closed, right_closed, expected):
    result = solve_service.solve_equation(
        "atanh(x)=asinh(x)", "x", domain="real",
        domain_lower=lower, domain_upper=upper,
        domain_lower_inclusive=left_closed, domain_upper_inclusive=right_closed,
    )
    assert [sp.sympify(s.text) for s in result.solutions] == expected


def test_inverse_hyperbolic_rejects_symbolic_requested_bounds_service():
    with pytest.raises(parsing.ParseSecurityError):
        solve_service.solve_equation("acosh(x)=asinh(x)", "x", domain="real",
                                     domain_lower="x", domain_upper="2")


@pytest.mark.parametrize("equation,expected", [
    ("atanh(x)=asinh(x)", ["0"]),
    ("acosh(x)=asinh(x)", []),
])
def test_inverse_hyperbolic_api(equation, expected):
    from fastapi.testclient import TestClient
    from app.main import app

    body = TestClient(app).post("/api/v1/solve", json={
        "equation": equation, "variable": "x", "domain": "real",
    }).json()
    assert body["success"] is True, body
    assert [s["text"] for s in body["result_data"]] == expected
