"""SY-Q-07 independent mathematical oracle ONLY; not a Plus product route test."""
import json
from pathlib import Path
import sympy
ROWS={r["id"]:r for r in (json.loads(line) for line in
 (Path(__file__).resolve().parents[2]/"qa/certification/syntax309_cases.jsonl")
 .read_text(encoding="utf-8").splitlines() if line.strip())}
def test_syq07_strict_interval_reference_only():
 row=ROWS["SY-Q-07"]
 assert row["entrada"]=="x^{2}<4" and row["esperado"]==r"x\in(-2,2)"
 x=sympy.Symbol("x",real=True)
 strict=sympy.solve_univariate_inequality(x**2<4,x,relational=False)
 non_strict=sympy.solve_univariate_inequality(x**2<=4,x,relational=False)
 assert strict==sympy.Interval.open(-2,2)
 assert non_strict==sympy.Interval(-2,2)
 assert -2 not in strict and 2 not in strict and 0 in strict
