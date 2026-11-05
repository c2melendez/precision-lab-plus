"""AS-RAT-02: conjugate rationalization with an independent math oracle."""
import math
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app
from app.services.algebra_service import simplify_expression


def test_as_rat_02_conjugate_rationalization_independent_oracle():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert r"| AS-RAT-02 | N1 | \( \frac{1}{\sqrt{2}+1} \) | \( \sqrt{2}-1 \) |".replace(" ", "") in source.replace(" ", "")

    original = "1/(sqrt(2)+1)"
    expected = sp.sqrt(2)-1
    service = simplify_expression(original)
    assert sp.simplify(service.result_expr-expected) == 0

    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": original})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    actual = sp.sympify(payload["result_text"])
    assert sp.simplify(actual-expected) == 0

    root_two = math.sqrt(2)
    independent_expected = root_two-1
    for result in [float(service.result_expr), float(actual)]:
        assert result > 0
        assert abs(result-independent_expected) < 1e-12
        assert abs(result*(root_two+1)-1) < 1e-12
    assert abs((root_two-1)*(root_two+1)-1) < 1e-12
