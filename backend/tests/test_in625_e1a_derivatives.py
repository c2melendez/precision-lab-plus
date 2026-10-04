import sympy
from app.services.derivative_service import compute_derivative

def test_en_ca_12_backend_x_squared():
    r=compute_derivative("x^2","x",1)
    assert sympy.simplify(r.result_expr-2*sympy.Symbol("x"))==0

def test_en_ca_14_backend_sin_x():
    r=compute_derivative("sin(x)","x",1)
    assert sympy.simplify(r.result_expr-sympy.cos(sympy.Symbol("x")))==0
