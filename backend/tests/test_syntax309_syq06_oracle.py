"""SY-Q-06 reference oracle only; NOT Plus HTTP product certification.

Plus /solve currently handles equations, not ordered inequalities.
This independent exact SymPy oracle is a readiness check for future integration.
"""
import json
from pathlib import Path
import sympy

ROWS = {r["id"]: r for r in (json.loads(line) for line in
    (Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl")
    .read_text(encoding="utf-8").splitlines() if line.strip())}

def test_syq06_reference_interval_oracle_not_product_route():
    row = ROWS["SY-Q-06"]
    assert row["entrada"] == r"x^{2}\le4"
    assert row["esperado"] == r"x\in[-2,2]"
    x = sympy.Symbol("x", real=True)
    assert sympy.solve_univariate_inequality(x**2 <= 4, x, relational=False) == sympy.Interval(-2, 2)
    assert sympy.solve_univariate_inequality(x**2 < 4, x, relational=False) == sympy.Interval.open(-2, 2)
