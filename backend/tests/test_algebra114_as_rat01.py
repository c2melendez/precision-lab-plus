"""AS-RAT-01: inverse square root rationalization with an independent math oracle."""
import math
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app
from app.services.algebra_service import simplify_expression


def test_as_rat_01_rationalize_inverse_sqrt_two_independent_oracle():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert r"| AS-RAT-01 | N1 | \( \frac{1}{\sqrt{2}} \) | \( \frac{\sqrt{2}}{2} \) |".replace(" ", "") in source.replace(" ", "")

    original = "1/sqrt(2)"
    expected = sp.sqrt(2) / 2
    service = simplify_expression(original)
    assert service.result_expr == expected

    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": original})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    actual = sp.sympify(payload["result_text"])
    assert sp.simplify(actual-expected) == 0

    # math.sqrt is independent of the symbolic CAS used by the service.
    independent_expected = math.sqrt(2) / 2
    for result in [float(service.result_expr), float(actual)]:
        assert result > 0
        assert abs(result-independent_expected) < 1e-12
        assert abs(result*result-0.5) < 1e-12
