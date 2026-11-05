"""AS-RAT-05: cubic radical conjugate with an independent math oracle."""
import math
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app
from app.services.algebra_service import simplify_expression


def test_as_rat_05_cubic_conjugate_service_http_independent_oracle():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    expected_row = (
        r"| AS-RAT-05 | N2 | \(\frac{1}{\sqrt[3]{2}+1}\) | "
        r"\(\frac{\sqrt[3]{4}-\sqrt[3]{2}+1}{3}\) |"
    )
    assert expected_row.replace(" ", "") in source.replace(" ", "")

    original = "1/(2**(1/3)+1)"
    service = simplify_expression(original)
    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": original})

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload

    # Preserve an exact symbolic contract check, but do not use SymPy as the
    # numeric expected-value oracle.
    t = sp.real_root(2, 3)
    exact_expected = (t * t - t + 1) / 3
    assert sp.simplify(service.result_expr - exact_expected) == 0
    http_expr = sp.sympify(payload["result_text"])
    assert sp.simplify(http_expr - exact_expected) == 0

    # Independent standard-library numeric oracle via real cube roots.
    root_two = math.cbrt(2.0)
    root_four = math.cbrt(4.0)
    independent_expected = (root_four - root_two + 1.0) / 3.0
    service_value = float(service.result_expr)
    http_value = float(http_expr)

    assert root_two > 0 and root_four > 0
    assert math.isclose(root_two**3, 2.0, rel_tol=1e-13, abs_tol=1e-13)
    assert math.isclose(root_four**3, 4.0, rel_tol=1e-13, abs_tol=1e-13)
    assert math.isclose(
        (root_two + 1.0) * (root_four - root_two + 1.0),
        3.0,
        rel_tol=1e-13,
        abs_tol=1e-13,
    )

    for actual in (service_value, http_value):
        assert actual > 0
        assert math.isclose(actual, independent_expected, rel_tol=1e-12, abs_tol=1e-12)
        assert math.isclose(actual * (root_two + 1.0), 1.0, rel_tol=1e-12, abs_tol=1e-12)
