"""AS-PAR-04: x^2 - 2*m*x + m^2 - 1 = 0, roots m +/- 1 via service and HTTP."""

from pathlib import Path

import sympy
from fastapi.testclient import TestClient

from app.main import app
from app.services.solve_service import solve_equation

client = TestClient(app)


def _solve_http(equation: str):
    return client.post(
        "/api/v1/solve",
        json={"equation": equation, "variable": "x", "angle_unit": "rad"},
    )


def _roots(result):
    return [sympy.sympify(item.text) for item in result.solutions]


def test_as_par_04_original_parameter_quadratic_service_and_http():
    source = (
        Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md"
    ).read_text()
    assert "| AS-PAR-04 | N2 |" in source

    x, m = sympy.symbols("x m")
    equation = "x^2-2*m*x+m^2-1=0"
    polynomial = x**2 - 2*m*x + m**2 - 1

    result = solve_equation(equation, "x")
    roots = _roots(result)
    assert len(roots) == 2
    assert all(sympy.simplify(polynomial.subs(x, root)) == 0 for root in roots)
    assert sympy.simplify(roots[0] - roots[1]) in (2, -2)

    response = _solve_http(equation)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    assert len(payload["result_data"]) == 2
    http_roots = [sympy.sympify(item["text"]) for item in payload["result_data"]]
    assert all(sympy.simplify(polynomial.subs(x, root)) == 0 for root in http_roots)
    assert sympy.simplify(http_roots[0] - http_roots[1]) in (2, -2)

    # m = 0 -> roots {-1, 1}.
    at_zero = {sympy.simplify(root.subs(m, 0)) for root in roots}
    assert at_zero == {sympy.Integer(-1), sympy.Integer(1)}

    # m = 2 -> roots {1, 3}.
    at_two = {sympy.simplify(root.subs(m, 2)) for root in roots}
    assert at_two == {sympy.Integer(1), sympy.Integer(3)}

    # The same concrete controls must be exposed over the HTTP boundary.
    zero_http = _solve_http("x^2-1=0")
    assert zero_http.status_code == 200, zero_http.text
    zero_http_roots = {
        sympy.simplify(sympy.sympify(item["text"]))
        for item in zero_http.json()["result_data"]
    }
    assert zero_http_roots == {sympy.Integer(-1), sympy.Integer(1)}

    two_http = _solve_http("x^2-4*x+3=0")
    assert two_http.status_code == 200, two_http.text
    two_http_roots = {
        sympy.simplify(sympy.sympify(item["text"]))
        for item in two_http.json()["result_data"]
    }
    assert two_http_roots == {sympy.Integer(1), sympy.Integer(3)}
