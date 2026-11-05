"""AS-RAT-03: two-radical conjugate rationalization and independent math oracle."""
import math
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app
from app.services.algebra_service import simplify_expression


def test_as_rat_03_two_radical_conjugate_service_http_independent_oracle():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    expected_row = r"| AS-RAT-03 | N2 | \(\frac{1}{\sqrt{2}+\sqrt{3}}\) | \(\sqrt{3}-\sqrt{2}\) |"
    assert expected_row.replace(" ", "") in source.replace(" ", "")

    expression = "1/(sqrt(2)+sqrt(3))"
    expected_symbolic = sp.sqrt(3) - sp.sqrt(2)
    service = simplify_expression(expression)
    assert sp.simplify(service.result_expr - expected_symbolic) == 0

    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": expression})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    http_expr = sp.sympify(payload["result_text"])
    assert sp.simplify(http_expr - expected_symbolic) == 0

    # math.sqrt is independent of the symbolic CAS.
    root_two = math.sqrt(2.0)
    root_three = math.sqrt(3.0)
    independent_expected = root_three - root_two
    service_value = float(service.result_expr)
    http_value = float(http_expr)

    assert independent_expected > 0
    assert math.isclose((root_three - root_two) * (root_three + root_two), 1.0, rel_tol=1e-13, abs_tol=1e-13)
    for actual in (service_value, http_value):
        assert actual > 0
        assert math.isclose(actual, independent_expected, rel_tol=1e-12, abs_tol=1e-12)
        assert math.isclose(actual * (root_two + root_three), 1.0, rel_tol=1e-12, abs_tol=1e-12)
