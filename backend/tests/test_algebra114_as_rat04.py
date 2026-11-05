"""AS-RAT-04: cube-root denominator rationalization with an independent math oracle."""
import math
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app
from app.services.algebra_service import simplify_expression


def test_as_rat_04_cube_root_denominator_service_http_independent_oracle():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    expected_row = r"| AS-RAT-04 | N2 | \(\frac{1}{\sqrt[3]{2}}\) | \(\frac{\sqrt[3]{4}}{2}\) |"
    assert expected_row.replace(" ", "") in source.replace(" ", "")

    original = "1/(2**(1/3))"
    expected_symbolic = sp.real_root(4, 3) / 2
    service = simplify_expression(original)
    assert sp.simplify(service.result_expr - expected_symbolic) == 0

    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": original})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    http_expr = sp.sympify(payload["result_text"])
    assert sp.simplify(http_expr - expected_symbolic) == 0

    # math.cbrt is independent from the symbolic CAS.
    independent_expected = math.cbrt(4.0) / 2.0
    service_value = float(service.result_expr)
    http_value = float(http_expr)
    assert independent_expected > 0
    assert math.isclose(independent_expected**3, 0.5, rel_tol=1e-12, abs_tol=1e-12)
    for actual in (service_value, http_value):
        assert actual > 0
        assert math.isclose(actual, independent_expected, rel_tol=1e-12, abs_tol=1e-12)
        assert math.isclose(actual**3, 0.5, rel_tol=1e-12, abs_tol=1e-12)
