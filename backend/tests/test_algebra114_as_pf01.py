"""AS-PF-01 service-level partial fractions; HTTP/UI exposure not yet certified."""
from pathlib import Path
import sympy as sp
from app.services.algebra_service import partial_fraction_expression


def test_as_pf_01_exact_partial_fractions_service():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-PF-01 | N2 |" in source
    result = partial_fraction_expression("(3*x+5)/((x+1)*(x+2))", "x")
    x = sp.Symbol("x")
    expected = 2/(x+1) + 1/(x+2)
    assert sp.cancel(result.result_expr - expected) == 0
    assert result.result_expr != result.input_expr
    assert sp.apart(result.result_expr, x) == expected
    assert result.steps and result.has_detailed_steps is False
