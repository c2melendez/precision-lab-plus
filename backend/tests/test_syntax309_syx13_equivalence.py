"""SY-X-13 original nested-power derivative oracle, symbolic equivalence."""
import json
from pathlib import Path
import sympy as sp
from app.services.derivative_service import compute_derivative

def test_syx13_original_nested_power_derivative_equivalent():
    lines=(Path(__file__).resolve().parents[2]/"qa/certification/syntax309_cases.jsonl").read_text().splitlines()
    row=next(json.loads(line) for line in lines if json.loads(line)["id"]=="SY-X-13")
    assert row["entrada"]==r"\frac{d}{dx}x^{x^{x}}"
    assert row["esperado"]==r"x^{x^{x}}\left(x^{x}(\ln x+1)\ln x+x^{x-1}\right)"
    x=sp.Symbol("x",positive=True)
    expected=x**(x**x)*(x**x*(sp.log(x)+1)*sp.log(x)+x**(x-1))
    actual=compute_derivative("x**(x**x)","x",1)
    assert sp.simplify(actual.result_expr.subs(sp.Symbol("x"),x)-expected)==0
