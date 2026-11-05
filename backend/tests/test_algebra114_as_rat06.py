"""AS-RAT-06: variable radical quotient, original domain and independent oracle."""
import math
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app
from app.services.algebra_service import simplify_expression


def test_as_rat_06_variable_radical_quotient_service_http_independent_oracle():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    expected_row = (
        r"| AS-RAT-06 | N2 | \\(\\frac{\\sqrt{x+h}-\\sqrt{x}}{h}\\) | "
        r"\\(\\frac{1}{\\sqrt{x+h}+\\sqrt{x}}\\), con "
        r"\\(x>0\\), \\(h>-x\\), \\(h\\neq0\\) |"
    )
    assert expected_row.replace(" ", "") in source.replace(" ", "")

    x, h = sp.symbols("x h")
    original = "(sqrt(x+h)-sqrt(x))/h"
    expected_symbolic = 1 / (sp.sqrt(x + h) + sp.sqrt(x))
    service = simplify_expression(original)
    assert sp.simplify(service.result_expr - expected_symbolic) == 0

    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": original})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    http_expr = sp.sympify(payload["result_text"])
    assert sp.simplify(http_expr - expected_symbolic) == 0

    samples = [(1, 1), (4, 0.5), (9, -2), (0.25, 2), (16, -3), (0.5, -0.25), (25, 5)]
    for xx, hh in samples:
        assert xx > 0 and hh > -xx and hh != 0

        service_value = float(sp.N(service.result_expr.subs({x: xx, h: hh})))
        http_value = float(sp.N(http_expr.subs({x: xx, h: hh})))

        # Standard-library math.sqrt is independent of the symbolic CAS.
        root_xh = math.sqrt(xx + hh)
        root_x = math.sqrt(xx)
        independent_conjugate = 1.0 / (root_xh + root_x)
        independent_original = (root_xh - root_x) / hh

        for actual in (service_value, http_value):
            assert actual > 0
            assert math.isclose(actual, independent_conjugate, rel_tol=1e-12, abs_tol=1e-12)
        assert math.isclose(independent_conjugate, independent_original, rel_tol=1e-12, abs_tol=1e-12)
