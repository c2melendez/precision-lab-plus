"""AS-DIV-08: symbolic cubic division with parameters, exact quotient/remainder and HTTP."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.algebra_service import simplify_expression


def test_as_div_08_original_symbolic_parameter_division_service_http():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-DIV-08 | N3 |" in source

    x, a, b, c = sp.symbols("x a b c")
    numerator, denominator = x**3 + a*x**2 + b*x + c, x - 1
    quotient_expected = x**2 + (a + 1)*x + (a + b + 1)
    remainder_expected = a + b + c + 1

    quotient, remainder = sp.div(numerator, denominator, x)
    assert sp.expand(quotient - quotient_expected) == 0
    assert sp.expand(remainder - remainder_expected) == 0
    assert sp.expand(numerator - denominator*quotient - remainder) == 0
    assert denominator.subs(x, 1) == 0
    assert sp.expand(numerator.subs(x, 1) - remainder_expected) == 0

    expected = quotient_expected + remainder_expected/denominator
    service = simplify_expression("(x**3+a*x**2+b*x+c)/(x-1)")
    assert sp.simplify(service.result_expr - expected) == 0

    # Numeric substitutions independently exercise the quotient/remainder identity.
    for av, bv, cv in ((2, -3, 4), (-2, 5, 0), (0, 0, 0)):
        remainder_value = av + bv + cv + 1
        for xx in (-3, -2, 0, 2, 3, 5):
            quotient_value = xx**2 + (av + 1)*xx + (av + bv + 1)
            numerator_value = xx**3 + av*xx**2 + bv*xx + cv
            expected_value = quotient_value + remainder_value/(xx - 1)
            actual_value = service.result_expr.subs({a: av, b: bv, c: cv, x: xx})
            assert abs(float(sp.N(actual_value)) - float(sp.N(expected_value))) < 1e-9
            assert numerator_value - (xx - 1)*quotient_value == remainder_value
        # x = 1 remains excluded because the original denominator is zero.
        assert denominator.subs(x, 1) == 0

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/simplify",
            json={"expression": "(x**3+a*x**2+b*x+c)/(x-1)"},
        )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    assert sp.simplify(sp.sympify(payload["result_text"]) - expected) == 0
