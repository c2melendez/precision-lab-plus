"""AS-PAR-01: parameter equation ax=b, including both degenerate cases, service and HTTP."""

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


def test_as_par_01_original_parameter_equation_service_and_http():
    source = (
        Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md"
    ).read_text()
    assert "| AS-PAR-01 | N2 |" in source

    x, a, b = sympy.symbols("x a b")

    # Generic parameter case: for a != 0, x = b/a.
    result = solve_equation("a*x=b", "x")
    assert len(result.solutions) == 1
    root = sympy.sympify(result.solutions[0].text)
    assert sympy.simplify(a * root - b) == 0

    response = _solve_http("a*x=b")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    assert len(payload["result_data"]) == 1
    http_root = sympy.sympify(payload["result_data"][0]["text"])
    assert sympy.simplify(a * http_root - b) == 0

    # Concrete non-degenerate case: 2x = 6 -> x = 3.
    numeric = solve_equation("2*x=6", "x")
    assert len(numeric.solutions) == 1
    assert sympy.simplify(sympy.sympify(numeric.solutions[0].text) - 3) == 0

    # a = 0, b = 0: identity, so every real x is a solution.
    identity = solve_equation("0*x=0", "x")
    assert identity.result_type == ResultType.IDENTITY
    assert identity.solutions == []
    identity_http = _solve_http("0*x=0")
    assert identity_http.status_code == 200, identity_http.text
    assert identity_http.json()["success"] is True
    assert identity_http.json()["result_type"] == "identity"

    # a = 0, b != 0: contradiction, so no solution exists.
    contradiction = solve_equation("0*x=5", "x")
    assert contradiction.result_type == ResultType.CONTRADICTION
    assert contradiction.solutions == []
    contradiction_http = _solve_http("0*x=5")
    assert contradiction_http.status_code == 200, contradiction_http.text
    assert contradiction_http.json()["success"] is True
    assert contradiction_http.json()["result_type"] == "contradiction"
