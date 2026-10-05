from app.services import parsing, solve_service, phase2_service
import sympy

def test_en_di_01_expression():
    e=parsing.parse_expression_tree("x^2-4",allow_equation=False)
    assert str(e) in {"x**2 - 4","x**2-4"}

def test_en_di_02_03_equations():
    r1=solve_service.solve_equation("x^2-4=0","x")
    r2=solve_service.solve_equation("x^2=4","x")
    assert {s.exact_text for s in r1.solutions} == {"-2","2"}
    assert {s.exact_text for s in r2.solutions} == {"-2","2"}

def test_en_di_04_inequality():
    rel=parsing.parse_inequality_tree("x^2>4")
    out=phase2_service.compute_inequality(rel,"x")
    assert out.solution_set == sympy.Union(sympy.Interval.open(-sympy.oo,-2),sympy.Interval.open(2,sympy.oo))

def test_en_di_05_absolute_inequality():
    rel=parsing.parse_inequality_tree("abs(x-1)<=2")
    out=phase2_service.compute_inequality(rel,"x")
    assert out.solution_set == sympy.Interval(-1,3)

def test_en_di_06_chained_inequalities():
    # El parser/router debe preservar la semántica de ambas comparaciones.
    x=sympy.Symbol("x")
    strict=sympy.And(x>3,x<7)
    closed=sympy.And(x>=3,x<=7)
    assert sympy.reduce_inequalities(strict,x) == sympy.And(x>3,x<7)
    assert sympy.reduce_inequalities(closed,x) == sympy.And(x>=3,x<=7)
