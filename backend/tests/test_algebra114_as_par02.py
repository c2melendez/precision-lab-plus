"""AS-PAR-02: (a-1)x=a+1, generic solution and the a=1 no-solution case."""

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


def test_as_par_02_original_parameter_equation_service_and_http():
    source = (
        Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md"
    ).read_text()
    assert "| AS-PAR-02 | N2 |" in source

    x, a = sympy.symbols("x a")

    # Generic case: a != 1, x = (a+1)/(a-1).
    result = solve_equation("(a-1)*x=a+1", "x")
    assert len(result.solutions) == 1
    root = sympy.sympify(result.solutions[0].text)
    assert sympy.simplify((a - 1) * root - (a + 1)) == 0

    response = _solve_http("(a-1)*x=a+1")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    assert len(payload["result_data"]) == 1
    http_root = sympy.sympify(payload["result_data"][0]["text"])
    assert sympy.simplify((a - 1) * http_root - (a + 1)) == 0

    # a = 0: -x = 1 -> x = -1.
    zero_parameter = solve_equation("-x=1", "x")
    assert len(zero_parameter.solutions) == 1
    assert sympy.simplify(sympy.sympify(zero_parameter.solutions[0].text) + 1) == 0

    # a = 2: x = 3.
    non_unit_parameter = solve_equation("x=3", "x")
    assert len(non_unit_parameter.solutions) == 1
    assert sympy.simplify(sympy.sympify(non_unit_parameter.solutions[0].text) - 3) == 0

    # a = 1: 0*x = 2, contradiction and no solution.
    degenerate = solve_equation("0*x=2", "x")
    assert degenerate.result_type == ResultType.CONTRADICTION
    assert degenerate.solutions == []

    degenerate_http = _solve_http("0*x=2")
    assert degenerate_http.status_code == 200, degenerate_http.text
    assert degenerate_http.json()["success"] is True
    assert degenerate_http.json()["result_type"] == "contradiction"
