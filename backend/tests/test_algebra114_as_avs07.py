"""Algebra114 AS-AVS-07: |x| = x-1 has no real solution; x=1/2 is extraneous."""

from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.responses import ResultType
from app.services.solve_service import solve_equation

x = sp.Symbol("x")
EQUATION = "abs(x)=x-1"


def test_as_avs_07_source_row():
    root = Path(__file__).resolve().parents[2]
    source = (root / "qa/certification/algebra114_source.md").read_text(encoding="utf-8")
    assert (
        "| AS-AVS-07 | N3 | \\(|x|=x-1\\) | Sin solución; si se eleva al cuadrado aparece "
        "\\(x=\\frac{1}{2}\\), que es extraña |"
    ) in source


def test_as_avs_07_extraneous_candidate_is_genuinely_extraneous():
    squared = sp.solve(sp.Eq(x**2, (x - 1) ** 2), x)
    assert squared == [sp.Rational(1, 2)]
    assert abs(sp.Rational(1, 2)) != sp.Rational(1, 2) - 1


def test_as_avs_07_no_solution_service_and_http():
    result = solve_equation(EQUATION, "x")
    assert result.result_type == ResultType.CONTRADICTION
    assert result.solutions == []
    assert result.has_detailed_steps is True
    text = " ".join(step.description for step in result.steps)
    assert "1/2" in text and "descarta" in text, text

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/solve", json={"equation": EQUATION, "variable": "x", "angle_unit": "rad"}
        )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    assert payload["result_type"] == "contradiction"
    assert not payload["result_data"]
    http_text = " ".join(step["description"] for step in payload["steps"])
    assert "1/2" in http_text and "descarta" in http_text


def test_as_avs_07_case_solver_scope_keeps_interval_identities_unsupported():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/solve",
            json={"equation": "abs(x-1)+abs(x-5)=4", "variable": "x", "angle_unit": "rad"},
        )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is False
    assert payload["error_code"] == "UNSUPPORTED_OPERATION"
