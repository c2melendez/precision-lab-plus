"""SY-R-09: public evaluate/integral output is reentered into real derivative requests."""
import os
import pytest
import sympy as sp
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse

def post(client, endpoint, **payload):
    response = client.post("/api/v1/" + endpoint, json=payload)
    assert response.status_code == 200, response.text
    result = MathResponse.model_validate(response.json())
    assert result.success and result.result_type.value == "scalar" and result.result_latex, result
    assert not sp.sympify(result.result_text).has(sp.Float), result
    return result

@pytest.mark.parametrize("source, variable, expected, derivative, dc", [
    ("x^3/3+C", "x", "x^3/3+C", "x^2", 1),
    ("y^4/4+C", "y", "y^4/4+C", "y^3", 1),
    ("(x^3)/(3)+C", "x", "x^3/3+C", "x^2", 1),
    ("(y^4)/(4)+C", "y", "y^4/4+C", "y^3", 1),
    ("x^3/3+7*C", "x", "x^3/3+7*C", "x^2", 7),
])
def test_syr09_exact_constant_reentry_and_real_derivative(source, variable, expected, derivative, dc):
    with TestClient(app) as client:
        result = post(client, "evaluate", expression=source)
        assert sp.simplify(sp.sympify(result.result_text) - sp.sympify(expected)) == 0, result
        assert sp.Symbol("C") in sp.sympify(result.result_text).free_symbols, result
        restored = post(client, "evaluate", expression=result.result_text)
        assert sp.simplify(sp.sympify(restored.result_text) - sp.sympify(expected)) == 0, restored
        dx = post(client, "derivative", expression=restored.result_text, variable=variable, order=1)
        assert dx.operation.value == "derivative", dx
        assert sp.simplify(sp.sympify(dx.result_text) - sp.sympify(derivative)) == 0, dx
        again = post(client, "evaluate", expression=dx.result_text)
        assert sp.simplify(sp.sympify(again.result_text) - sp.sympify(derivative)) == 0, again
        constant = post(client, "derivative", expression=restored.result_text, variable="C", order=1)
        assert sp.sympify(constant.result_text) == dc, constant

def test_syr09_actual_integral_response_reentered_into_derivative():
    with TestClient(app) as client:
        integral = post(client, "integral", expression="x^2", variable="x")
        assert sp.simplify(sp.sympify(integral.result_text) - sp.sympify("x^3/3+C")) == 0, integral
        result = post(client, "derivative", expression=integral.result_text, variable="x", order=1)
        assert sp.simplify(sp.sympify(result.result_text) - sp.sympify("x^2")) == 0, result
