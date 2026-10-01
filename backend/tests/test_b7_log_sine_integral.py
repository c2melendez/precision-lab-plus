"""A convergent definite integral may be known without an elementary primitive."""
import os

os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")

import mpmath as mp
import pytest
import sympy as sp

from app.services import integral_service


@pytest.mark.parametrize("variable,lower,upper,sign", [
    ("x", "0", "pi/2", -1),
    ("x", "0", "(pi)/(2)", -1),
    ("x", "pi/2", "0", 1),
    ("t", "0", "pi/2", -1),
])
def test_log_sine_definite_identity_service(variable, lower, upper, sign):
    result = integral_service.integrate_expression(f"ln(sin({variable}))", variable, lower, upper)
    assert result.is_definite is True
    assert result.definite_value == sign*sp.pi*sp.log(2)/2
    assert result.definite_value.is_finite is True
    assert not result.definite_value.has(sp.Integral)
    assert result.antiderivative is None
    assert result.steps == []
    assert result.has_detailed_steps is False
    assert result.input_expr == sp.log(sp.sin(sp.Symbol(variable)))


def test_log_sine_value_matches_independent_quadrature_service():
    result = integral_service.integrate_expression("ln(sin(x))", "x", "0", "pi/2")
    with mp.workdps(40):
        integral = mp.quad(lambda x: mp.log(mp.sin(x)), [0, mp.pi/4, mp.pi/2])
        exact = mp.mpf(str(sp.N(result.definite_value, 40)))
        assert abs(integral-exact) < mp.mpf("1e-38")


@pytest.mark.parametrize("expression,coefficient", [
    ("log(sin(x))", 1/sp.log(10)),
    ("2*ln(sin(x))", 2),
    ("-ln(sin(x))", -1),
])
def test_log_sine_linearity_preserves_calculator_log_base_service(expression, coefficient):
    result = integral_service.integrate_expression(expression, "x", "0", "pi/2")
    assert sp.simplify(result.definite_value+coefficient*sp.pi*sp.log(2)/2) == 0


def test_definite_singularity_guard_still_rejects_divergence_service():
    with pytest.raises(integral_service.DivergentIntegralError):
        integral_service.integrate_expression("1/sin(x)", "x", "0", "pi/2")


@pytest.mark.parametrize("lower,upper,sign", [("0", "pi/2", -1), ("pi/2", "0", 1)])
def test_log_sine_definite_api_has_exact_value_without_primitive(lower, upper, sign):
    from fastapi.testclient import TestClient
    from app.main import app

    body = TestClient(app).post("/api/v1/integral", json={
        "expression": "ln(sin(x))", "variable": "x",
        "lower_bound": lower, "upper_bound": upper,
    }).json()
    assert body["success"] is True, body
    assert sp.simplify(sp.sympify(body["result_text"])-sign*sp.pi*sp.log(2)/2) == 0
    assert "Integral" not in body["result_text"]
    assert body["antiderivative_expression"] is None
    assert body["antiderivative_latex"] is None
