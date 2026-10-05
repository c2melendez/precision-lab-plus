from app.schemas.responses import ResultType
from app.services import solve_service

def classify(equation):
    return solve_service.solve_equation(equation, None, "rad").result_type

def test_en_di_19_true_false():
    assert classify("1=1") == ResultType.IDENTITY
    assert classify("2=3") == ResultType.CONTRADICTION

def test_en_di_20_identity_and_no_solution():
    assert classify("x=x") == ResultType.IDENTITY
    assert classify("x+1=x") == ResultType.CONTRADICTION

def test_en_di_21_trig_identity():
    assert classify("sin(x)**2+cos(x)**2=1") == ResultType.IDENTITY

def test_en_di_23_binomial_identity():
    assert classify("(x+1)**2=x**2+2*x+1") == ResultType.IDENTITY
