from app.services import parsing
import sympy

def test_en_mt_14_piecewise_semantics():
    x=sympy.Symbol("x")
    left=parsing.parse_expression_tree("x^2", allow_equation=False)
    right=parsing.parse_expression_tree("x", allow_equation=False)
    cond_left=parsing.parse_inequality_tree("x<0")
    cond_right=parsing.parse_inequality_tree("x>=0")
    piece=sympy.Piecewise((left, cond_left),(right, cond_right))
    assert piece.subs(x,-2) == 4
    assert piece.subs(x,3) == 3
