"""Algebra114 AS-RAT-08 nested radical denesting with an independent math oracle."""
import math
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app
from app.services.algebra_service import simplify_expression


def test_as_rat_08_nested_radical_original_service_http_independent_oracle():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    expected_row = r"| AS-RAT-08 | N3 | \(\sqrt{5+2\sqrt{6}}\) | \(\sqrt{3}+\sqrt{2}\) |"
    assert expected_row.replace(" ", "") in source.replace(" ", "")

    original = "sqrt(5+2*sqrt(6))"
    expected_symbolic = sp.sqrt(3) + sp.sqrt(2)
    service = simplify_expression(original)
    assert sp.simplify(service.result_expr - expected_symbolic) == 0

    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": original})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    http_expr = sp.sympify(payload["result_text"])
    assert sp.simplify(http_expr - expected_symbolic) == 0

    # Independent numerical witnesses from Python math, not the symbolic CAS.
    root_two = math.sqrt(2.0)
    root_three = math.sqrt(3.0)
    root_six = math.sqrt(6.0)
    independent_denested = root_three + root_two
    independent_original = math.sqrt(5.0 + 2.0 * root_six)
    for actual in (float(service.result_expr), float(http_expr)):
        assert actual > 0
        assert math.isclose(actual, independent_denested, rel_tol=1e-12, abs_tol=1e-12)
        assert math.isclose(actual, independent_original, rel_tol=1e-12, abs_tol=1e-12)
        assert math.isclose(actual * actual, 5.0 + 2.0 * root_six, rel_tol=1e-12, abs_tol=1e-12)
    assert math.isclose(independent_denested * independent_denested, 5.0 + 2.0 * root_six, rel_tol=1e-12, abs_tol=1e-12)
