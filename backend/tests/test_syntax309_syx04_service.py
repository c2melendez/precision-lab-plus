"""SY-X-04: prove 500 explicit addends at the mathematical service boundary.

This intentionally bypasses FastAPI's 500-character request schema, without
changing that schema. HTTP acceptance still requires separate authorization.
"""
import sympy
import pytest

from app.services import evaluate_service
from app.services.parsing import ParseSecurityError


@pytest.mark.xfail(strict=True, raises=ParseSecurityError,
                  reason="SY-X-04 BLOCKED: parser contract max_length=500 rejects 999 characters; preserve the 500x oracle")
def test_syx04_full_source_math_service_without_http_shortcut():
    source = "+".join(["x"] * 500)
    assert len(source) == 999
    assert source.count("x") == 500
    assert source.count("+") == 499

    output = evaluate_service.evaluate(source, "rad", None)
    expected = 500 * sympy.Symbol("x")
    assert sympy.simplify(output.expr - expected) == 0


def test_syx04_math_service_recovers_for_a_new_expression():
    source = "+".join(["x"] * 500)
    with pytest.raises(ParseSecurityError, match="500 caracteres"):
        evaluate_service.evaluate(source, "rad", None)
    recovered = evaluate_service.evaluate("2+3", "rad", None)
    assert sympy.simplify(recovered.expr - sympy.Integer(5)) == 0
