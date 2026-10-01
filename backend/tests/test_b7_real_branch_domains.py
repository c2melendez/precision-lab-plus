"""B7 regressions for real inverse-function branches and domains."""
import os

os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")

import pytest
import sympy as sp

from app.services import parsing, phase2_service


@pytest.mark.parametrize("point,expected", [
    ("-oo", sp.pi),
    ("0", sp.pi / 2),
    ("oo", sp.Integer(0)),
])
def test_arccot_limits_follow_calculator_real_branch(point, expected):
    result = phase2_service.compute_limit("acot(x)", "x", point, "both")
    assert result.dne is False
    assert sp.simplify(result.value - expected) == 0


@pytest.mark.parametrize("operator,right_open", [(">", True), (">=", False)])
def test_arcoth_inequality_excludes_undefined_pole(operator, right_open):
    relation = parsing.parse_inequality_tree(f"acoth(x){operator}ln(2)")
    result = phase2_service.compute_inequality(relation, "x")
    upper = sp.coth(sp.log(2))
    expected = sp.Interval(1, upper, left_open=True, right_open=right_open)
    assert result.solution_set == expected
    assert result.solution_set.contains(1) is sp.false
    assert result.solution_set.contains(sp.Rational(6, 5)) is sp.true
    assert result.solution_set.contains(2) is sp.false
