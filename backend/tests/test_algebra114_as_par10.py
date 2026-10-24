"""AS-PAR-10: x/(x-a)=1; preserve the original denominator restriction."""

from pathlib import Path

import sympy
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.responses import ResultType
from app.services.solve_service import solve_equation

client = TestClient(app)


def _solve_http(equation: str):
    return client.post(
        "/api/v1/solve",
        json={"equation": equation, "variable": "x", "angle_unit": "rad"},
    )


def test_as_par_10_original_rational_equation_service_and_http():
    source = (
        Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md"
    ).read_text()
    assert "| AS-PAR-10 | N3 |" in source
    assert r"\frac{x}{x-a}=1" in source
    assert "x\\neq0" in source

    # a != 0: x = x-a is impossible; no solution.
    equation = "x/(x-3)=1"
    result = solve_equation(equation, "x")
    assert result.result_type == ResultType.CONTRADICTION
    assert result.solutions == []
    response = _solve_http(equation)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    assert payload["result_type"] == "contradiction"
    # Public contract: contradiction/identity carry no solution list
    # (result_data is null, same as AS-PAR-01/02 contradictions).
    assert not payload["result_data"]

    # a = 0: the equation is an identity only on its original domain x != 0.
    equation = "x/x=1"
    result = solve_equation(equation, "x")
    assert result.result_type == ResultType.IDENTITY
    assert any(
        ("x≠0" in step.description or "x != 0" in step.description or "x\\neq0" in step.description)
        for step in result.steps
    ), "identity classification must retain the excluded point x=0"
    response = _solve_http(equation)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    assert payload["result_type"] == "identity"
    assert any(
        ("x≠0" in step.get("description", "") or "x != 0" in step.get("description", "") or "x\\neq0" in step.get("description", ""))
        for step in payload.get("steps", [])
    ), "HTTP response must preserve the original domain restriction"
