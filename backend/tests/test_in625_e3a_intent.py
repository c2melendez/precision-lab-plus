from app.services import parsing, solve_service, phase2_service
import sympy

def test_en_di_01_expression():
    e=parsing.parse_expression_tree("x^2-4",allow_equation=False)
    assert sympy.simplify(e - (sympy.Symbol("x")**2 - 4)) == 0

def test_en_di_02_03_equations():
    r1=solve_service.solve_equation("x^2-4=0","x")
    r2=solve_service.solve_equation("x^2=4","x")
    assert {s.text for s in r1.solutions} == {"-2","2"}
    assert {s.text for s in r2.solutions} == {"-2","2"}

def test_en_di_04_inequality():
    rel=parsing.parse_inequality_tree("x^2>4")
    out=phase2_service.compute_inequality(rel,"x")
    assert out.solution_set == sympy.Union(sympy.Interval.open(-sympy.oo,-2),sympy.Interval.open(2,sympy.oo))

def test_en_di_05_absolute_inequality():
    rel=parsing.parse_inequality_tree("abs(x-1)<=2")
    out=phase2_service.compute_inequality(rel,"x")
    assert out.solution_set == sympy.Interval(-1,3)

def test_en_di_06_chained_inequalities():
    strict = parsing.parse_chained_inequalities("3<x<7")
    closed = parsing.parse_chained_inequalities("3<=x<=7")
    assert strict is not None and closed is not None
    strict_result = phase2_service.compute_chained_inequality(strict, "x")
    closed_result = phase2_service.compute_chained_inequality(closed, "x")
    assert strict_result.solution_set == sympy.Interval.open(3, 7)
    assert closed_result.solution_set == sympy.Interval(3, 7)
