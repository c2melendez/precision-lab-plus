import sympy
from app.services import ode_service

x = sympy.Symbol("x")

def _rhs(result):
    return sympy.simplify(result.solution.rhs)

def test_en_di_12_first_order_growth():
    result = ode_service.solve_ode("y'=y")
    assert result.order == 1
    assert sympy.simplify(sympy.diff(_rhs(result), x) - _rhs(result)) == 0

def test_en_di_13_harmonic_oscillator():
    result = ode_service.solve_ode("y''+y=0")
    assert result.order == 2
    rhs = _rhs(result)
    assert sympy.simplify(sympy.diff(rhs, x, 2) + rhs) == 0

def test_en_di_14_dydx_normalized_contract():
    # El frontend normaliza \\frac{dy}{dx} a y' antes de /ode.
    result = ode_service.solve_ode("y'=y")
    assert result.order == 1
    assert sympy.simplify(sympy.diff(_rhs(result), x) - _rhs(result)) == 0
