"""
Tests reales del Módulo 5 para `POST /api/v1/integral` (spec, secciones 8.4
y 15): sin(x) con +C, integral definida (≥3 pasos), fallback por regla no
mapeada, límite `oo` -> mensaje exacto (sin prometer `/integral/improper`).
"""

import os

os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")

from fastapi.testclient import TestClient
import sympy as sp

from app.main import app
from app.services.integral_service import UNSUPPORTED_INFINITE_BOUNDS_MESSAGE

client = TestClient(app)


def _integral(expression, variable="x", lower_bound=None, upper_bound=None):
    payload = {"expression": expression, "variable": variable}
    if lower_bound is not None:
        payload["lower_bound"] = lower_bound
    if upper_bound is not None:
        payload["upper_bound"] = upper_bound
    return client.post("/api/v1/integral", json=payload)


def test_indefinite_sin_x_includes_plus_c():
    response = _integral("sin(x)")
    body = response.json()
    assert body["success"] is True
    assert body["has_detailed_steps"] is True
    assert body["result_text"].endswith("+ C")
    assert body["result_latex"].endswith("+ C")
    assert body["antiderivative_expression"] == "-cos(x)"
    assert "\\cos" in body["antiderivative_latex"]
    assert not body["antiderivative_latex"].endswith("+ C")
    assert any(step["rule"] == "SinRule" for step in body["steps"])


def test_trigonometric_integer_powers_are_actual_antiderivatives():
    x = sp.Symbol("x")
    for function in ("sin", "cos", "tan"):
        for exponent in (0, 1, 2, 3, 5):
            expression = f"{function}(x)^{exponent}"
            body = _integral(expression).json()
            assert body["success"] is True, expression
            antiderivative = sp.sympify(body["antiderivative_expression"])
            assert not antiderivative.has(sp.Integral), expression
            assert sp.simplify(sp.diff(antiderivative, x) - getattr(sp, function)(x)**exponent) == 0, expression


def test_symbolic_trig_power_does_not_claim_an_unevaluated_integral_is_solved():
    for function in ("sin", "cos", "tan"):
        body = _integral(f"{function}(x)^n").json()
        assert body["success"] is False
        assert body["error_code"] == "UNSUPPORTED_OPERATION"
        assert "exponente simbólico" in body["error_message"]


def test_definite_integral_minimum_three_steps():
    response = _integral("x**2", lower_bound="0", upper_bound="2")
    body = response.json()
    assert body["success"] is True
    assert body["has_detailed_steps"] is True
    assert len(body["steps"]) >= 3
    rule_names = [step["rule"] for step in body["steps"]]
    assert "FTC" in rule_names
    assert "EvaluateBounds" in rule_names
    # ∫[0,2] x**2 dx = 8/3
    assert body["result_text"] == "8/3"
    assert body["antiderivative_expression"] == "x**3/3"


def test_fallback_for_unmapped_rule_sin_of_sin():
    # sin(sin(x)) no tiene antiderivada elemental (manualintegrate ->
    # DontKnowRule) -> fallback completo a integrate() directo.
    response = _integral("sin(sin(x))")
    body = response.json()
    assert body["success"] is True
    assert body["has_detailed_steps"] is False
    assert body["steps"] == []
    assert any("directo de SymPy" in w for w in body["warnings"])


def test_infinite_upper_bound_returns_exact_message():
    response = _integral("exp(-x)", lower_bound="0", upper_bound="oo")
    body = response.json()
    assert body["success"] is False
    assert body["error_code"] == "UNSUPPORTED_IN_PHASE_1"
    assert body["error_message"] == UNSUPPORTED_INFINITE_BOUNDS_MESSAGE
    assert "/integral/improper" not in body["error_message"]


def test_infinite_lower_bound_returns_exact_message():
    response = _integral("exp(x)", lower_bound="-oo", upper_bound="0")
    body = response.json()
    assert body["success"] is False
    assert body["error_code"] == "UNSUPPORTED_IN_PHASE_1"
    assert body["error_message"] == UNSUPPORTED_INFINITE_BOUNDS_MESSAGE


def test_only_one_bound_is_validation_error():
    response = _integral("x**2", lower_bound="0")
    body = response.json()
    assert body["success"] is False
    assert body["error_code"] == "VALIDATION_ERROR"


def test_power_rule_labeled():
    response = _integral("x**3")
    body = response.json()
    assert body["success"] is True
    assert body["steps"][0]["title"] == "Integral de potencia"
    assert body["result_text"] == "x**4/4 + C"


def test_add_rule_produces_one_step_per_term():
    response = _integral("x**2 + sin(x)")
    body = response.json()
    assert body["success"] is True
    rule_names = [step["rule"] for step in body["steps"]]
    assert "PowerRule" in rule_names
    assert "SinRule" in rule_names


def test_integral_parse_error_propagates():
    response = _integral("eval(1)")
    body = response.json()
    assert body["success"] is False
    assert body["error_code"] == "PARSE_ERROR"
    assert body["operation"] == "integral"


def test_trig_power_notations_share_canonical_result():
    for function in ("sin", "cos", "tan"):
        conventional = _integral(f"{function}^3(x)").json()
        postfix = _integral(f"{function}(x)^3").json()
        assert conventional["success"] is True
        assert conventional["antiderivative_expression"] == postfix["antiderivative_expression"]
        assert conventional["result_latex"] == postfix["result_latex"]


def test_trig_definite_integral_uses_direct_fast_path():
    response = _integral("sin(x)", lower_bound="0", upper_bound="pi")
    body = response.json()
    assert body["success"] is True
    assert body["result_text"] == "2"
    assert body["has_detailed_steps"] is False
    assert any("directamente" in warning for warning in body["warnings"])


def test_definite_integral_crossing_trig_pole_is_domain_error():
    response = _integral("sec(x)^2", lower_bound="0", upper_bound="pi")
    body = response.json()
    assert body["success"] is False
    assert body["error_code"] == "DOMAIN_ERROR"


def test_endpoint_singularity_can_be_improper_but_convergent():
    response = _integral("1/(x*sqrt(x^2-1))", lower_bound="1", upper_bound="2")
    body = response.json()
    assert body["success"] is True
    assert sp.simplify(sp.sympify(body["result_text"]) - sp.pi/3) == 0


def test_endpoint_poles_still_reject_divergent_tan_integral():
    response = _integral("tan(x)", lower_bound="-pi/2", upper_bound="pi/2")
    body = response.json()
    assert body["success"] is False
    assert body["error_code"] == "DOMAIN_ERROR"


def test_fast_path_common_identities_are_exact_antiderivatives():
    x = sp.Symbol("x")
    cases = [
        ("sec(x)^2", sp.tan(x)),
        ("csc(x)^2", -sp.cot(x)),
        ("1/(1+x^2)", sp.atan(x)),
        ("1/sqrt(1-x^2)", sp.asin(x)),
        ("cosh(x)", sp.sinh(x)),
        ("tanh(x)", sp.log(sp.cosh(x))),
        ("sech(x)^2", sp.tanh(x)),
        ("csch(x)^2", -sp.coth(x)),
        ("sinh(x)*cosh(x)", sp.sinh(x) ** 2 / 2),
        ("x*cos(x)", x * sp.sin(x) + sp.cos(x)),
        ("x*sinh(x)", x * sp.cosh(x) - sp.sinh(x)),
        ("sin(x)^2", x / 2 - sp.sin(2 * x) / 4),
        ("sinh(x)^2", sp.sinh(2 * x) / 4 - x / 2),
        ("asinh(x)", x * sp.asinh(x) - sp.sqrt(x**2 + 1)),
        ("acosh(x)", x * sp.acosh(x) - sp.sqrt(x**2 - 1)),
        ("atanh(x)", x * sp.atanh(x) + sp.log(1 - x**2) / 2),
    ]
    for expression, expected in cases:
        body = _integral(expression).json()
        assert body["success"] is True, expression
        antiderivative = sp.sympify(body["antiderivative_expression"])
        assert sp.simplify(sp.diff(antiderivative, x) - sp.diff(expected, x)) == 0, expression
        assert not antiderivative.has(sp.Integral), expression


def test_fast_path_definite_common_identities():
    cases = [
        ("sin(x)", "0", "pi", sp.Integer(2)),
        ("1/(1+x^2)", "0", "1", sp.pi / 4),
        ("cosh(x)", "-1", "1", 2 * sp.sinh(1)),
        ("sech(x)^2", "0", "1", sp.tanh(1)),
        ("cos(x)/(1+sin(x)^2)", "0", "pi/2", sp.pi/4),
    ]
    for expression, lower, upper, expected in cases:
        body = _integral(expression, lower_bound=lower, upper_bound=upper).json()
        assert body["success"] is True, expression
        actual = sp.sympify(body["result_text"])
        assert sp.simplify(actual - expected) == 0, expression
