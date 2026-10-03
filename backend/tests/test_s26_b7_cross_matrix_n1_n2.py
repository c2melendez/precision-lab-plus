"""S26 B7 — recertificación N1/N2 cruzada.

Casos tomados de las matrices de trigonometría y log/exp/radicales.
La comparación es matemática (SymPy), no textual, para aceptar formas
equivalentes sin ocultar errores de dominio o cálculo.
"""

import sympy as sp

from app.services import derivative_service, integral_service, evaluate_service


x = sp.Symbol("x", real=True)


def _equivalent(actual: sp.Expr, expected: sp.Expr) -> bool:
    return sp.simplify(sp.trigsimp(actual - expected)) == 0


def test_n1_hyperbolic_log_known_values():
    # EV-H-04 / EV-H-05 / EV-H-06
    cases = [
        ("sinh(log(2))", sp.Rational(3, 4)),
        ("cosh(log(2))", sp.Rational(5, 4)),
        ("tanh(log(2))", sp.Rational(3, 5)),
    ]
    for expression, expected in cases:
        result = evaluate_service.evaluate(expression)
        assert result.is_numeric is True
        assert sp.simplify(result.expr - expected) == 0


def test_n1_hyperbolic_identity_is_preserved():
    # EV-H-12
    result = evaluate_service.evaluate("cosh(1)**2-sinh(1)**2")
    assert sp.simplify(result.expr - 1) == 0


def test_n2_derivative_log_sine_matches_cotangent():
    # DV-T-01
    result = derivative_service.compute_derivative("log(sin(x))", "x", 1)
    assert _equivalent(result.result_expr, sp.cot(x))


def test_n2_derivative_exp_sine_chain_rule():
    # DV-T-06
    result = derivative_service.compute_derivative("exp(sin(x))", "x", 1)
    expected = sp.cos(x) * sp.exp(sp.sin(x))
    assert _equivalent(result.result_expr, expected)


def test_n2_derivative_log_cosh_matches_tanh():
    # DV-T-14
    result = derivative_service.compute_derivative("log(cosh(x))", "x", 1)
    assert _equivalent(result.result_expr, sp.tanh(x))


def test_n2_integral_exp_sine_differentiates_back():
    # IT-T-01
    result = integral_service.integrate_expression("exp(x)*sin(x)", "x")
    assert _equivalent(sp.diff(result.antiderivative, x), sp.exp(x) * sp.sin(x))


def test_n2_integral_cos_over_one_plus_sin_squared_differentiates_back():
    # IT-T-09 / IT-D-18
    integrand = sp.cos(x) / (1 + sp.sin(x) ** 2)
    result = integral_service.integrate_expression("cos(x)/(1+sin(x)**2)", "x")
    assert _equivalent(sp.diff(result.antiderivative, x), integrand)


def test_n2_definite_exp_sine():
    # ID-M-06
    result = integral_service.integrate_expression("exp(x)*sin(x)", "x", "0", "pi")
    expected = (1 + sp.exp(sp.pi)) / 2
    assert result.definite_value is not None
    assert _equivalent(result.definite_value, expected)


def test_n2_radical_log_integral_differentiates_back():
    # IT-M-01
    integrand = sp.sqrt(x) * sp.log(x)
    result = integral_service.integrate_expression("sqrt(x)*log(x)", "x")
    assert _equivalent(sp.diff(result.antiderivative, x), integrand)
