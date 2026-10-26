"""AS-PAR-05: x^2 + m*x + 1 = 0 over R, discriminant branches via service and HTTP."""

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


def _http_roots(payload):
    return [sympy.sympify(item["text"]) for item in payload["result_data"]]


def _assert_original_equation(roots, x, m, parameter):
    polynomial = x**2 + m*x + 1
    assert all(sympy.simplify(polynomial.subs({x: root, m: parameter})) == 0 for root in roots)


def test_as_par_05_original_real_domain_parameter_quadratic_service_and_http():
    source = (
        Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md"
    ).read_text()
    assert "| AS-PAR-05 | N3 |" in source

    x, m = sympy.symbols("x m")
    polynomial = x**2 + m*x + 1

    # Generic roots satisfy the original polynomial; their squared separation
    # equals the discriminant, m^2 - 4.
    result = solve_equation("x^2+m*x+1=0", "x")
    roots = _roots(result)
    assert len(roots) == 2
    assert all(sympy.simplify(polynomial.subs(x, root)) == 0 for root in roots)
    assert sympy.simplify((roots[0] - roots[1]) ** 2 - (m**2 - 4)) == 0

    response = _solve_http("x^2+m*x+1=0")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    http_roots = _http_roots(payload)
    assert len(http_roots) == 2
    assert all(sympy.simplify(polynomial.subs(x, root)) == 0 for root in http_roots)
    assert sympy.simplify((http_roots[0] - http_roots[1]) ** 2 - (m**2 - 4)) == 0

    # |m| > 2: two exact real roots; check both signs and both service boundaries.
    for parameter in (3, -3):
        equation = f"x^2+({parameter})*x+1=0"
        discriminant = parameter**2 - 4
        expected = {
            sympy.simplify((-parameter + sympy.sqrt(discriminant)) / 2),
            sympy.simplify((-parameter - sympy.sqrt(discriminant)) / 2),
        }
        solved = solve_equation(equation, "x")
        service_roots = {sympy.simplify(root) for root in _roots(solved)}
        assert service_roots == expected
        assert all(item.is_complex is False for item in solved.solutions)
        _assert_original_equation(service_roots, x, m, parameter)

        http = _solve_http(equation)
        assert http.status_code == 200, http.text
        body = http.json()
        assert body["success"] is True, body
        http_items = body["result_data"]
        http_roots = {sympy.simplify(root) for root in _http_roots(body)}
        assert http_roots == expected
        assert all(item["is_complex"] is False for item in http_items)
        _assert_original_equation(http_roots, x, m, parameter)

    # |m| = 2: the two branches collapse to one distinct double root x = -m/2.
    for parameter, expected_root in ((2, sympy.Integer(-1)), (-2, sympy.Integer(1))):
        equation = f"x^2+({parameter})*x+1=0"
        solved = solve_equation(equation, "x")
        service_roots = _roots(solved)
        assert len(service_roots) == 1
        assert sympy.simplify(service_roots[0]) == expected_root
        assert sympy.simplify(polynomial.subs({x: expected_root, m: parameter})) == 0

        http = _solve_http(equation)
        assert http.status_code == 200, http.text
        body = http.json()
        assert body["success"] is True, body
        assert len(body["result_data"]) == 1
        assert sympy.simplify(_http_roots(body)[0]) == expected_root
        assert sympy.simplify(polynomial.subs({x: _http_roots(body)[0], m: parameter})) == 0

    # |m| < 2: there are no real roots. The general solver may still return
    # two complex roots; both must be identified as complex, never as real.
    for parameter in (0, 1, -1):
        equation = f"x^2+({parameter})*x+1=0"
        concrete_polynomial = polynomial.subs(m, parameter)
        assert sympy.solveset(concrete_polynomial, x, domain=sympy.S.Reals) == sympy.EmptySet

        solved = solve_equation(equation, "x")
        service_roots = _roots(solved)
        assert len(service_roots) == 2
        assert all(item.is_complex for item in solved.solutions)
        assert all(sympy.simplify(concrete_polynomial.subs(x, root)) == 0 for root in service_roots)

        http = _solve_http(equation)
        assert http.status_code == 200, http.text
        body = http.json()
        assert body["success"] is True, body
        http_items = body["result_data"]
        http_roots = _http_roots(body)
        assert len(http_roots) == 2
        assert all(item["is_complex"] is True for item in http_items)
        assert all(sympy.simplify(concrete_polynomial.subs(x, root)) == 0 for root in http_roots)
