import sympy
from app.services.integral_service import integrate_expression

def test_en_ca_01_x_squared_indefinite():
    r=integrate_expression("x^2","x")
    x=sympy.Symbol("x")
    assert sympy.simplify(r.antiderivative-x**3/3)==0

def test_en_ca_04_x_squared_zero_one():
    r=integrate_expression("x^2","x","0","1")
    assert sympy.simplify(r.definite_value-sympy.Rational(1,3))==0

def test_en_ca_06_sin_zero_pi():
    r=integrate_expression("sin(x)","x","0","pi")
    assert sympy.simplify(r.definite_value-2)==0

def test_en_ca_08_reciprocal_indefinite():
    r=integrate_expression("1/x","x")
    x=sympy.Symbol("x")
    assert sympy.simplify(sympy.diff(r.antiderivative,x)-1/x)==0

def test_en_ca_10_variable_t():
    r=integrate_expression("t","t")
    t=sympy.Symbol("t")
    assert sympy.simplify(r.antiderivative-t**2/2)==0
