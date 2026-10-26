"""AS-PAR-03: x^2=a over R, symbolic roots, nonnegative cases and negative-domain oracle."""

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


def test_as_par_03_original_real_domain_square_equation_service_and_http():
    source = (
        Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md"
    ).read_text()
    assert "| AS-PAR-03 | N2 |" in source

    x, a = sympy.symbols("x a")

    # Generic case: the two symbolic roots are +/-sqrt(a).
    result = solve_equation("x^2=a", "x")
    assert len(result.solutions) == 2
    roots = [sympy.sympify(item.text) for item in result.solutions]
    assert all(sympy.simplify(root**2 - a) == 0 for root in roots)
    assert sympy.simplify(roots[0] - roots[1]) != 0

    response = _solve_http("x^2=a")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    assert len(payload["result_data"]) == 2
    http_roots = [sympy.sympify(item["text"]) for item in payload["result_data"]]
    assert all(sympy.simplify(root**2 - a) == 0 for root in http_roots)

    # a = 4: the real roots are -2 and 2.
    positive = solve_equation("x^2=4", "x")
    positive_roots = {sympy.simplify(sympy.sympify(item.text)) for item in positive.solutions}
    assert positive_roots == {sympy.Integer(-2), sympy.Integer(2)}

    # a = 0: the only distinct root is 0.
    zero = solve_equation("x^2=0", "x")
    assert len(zero.solutions) == 1
    assert sympy.simplify(sympy.sympify(zero.solutions[0].text)) == 0

    # a < 0: the canonical source is explicitly over R, so there are no
    # real roots. The general solver supports complex roots, which must be
    # identified as complex rather than mistaken for real solutions.
    assert sympy.solveset(x**2 + 1, x, domain=sympy.S.Reals) == sympy.EmptySet
    negative = solve_equation("x^2=-1", "x")
    assert len(negative.solutions) == 2
    assert all(item.is_complex for item in negative.solutions)
    negative_http = _solve_http("x^2=-1")
    assert negative_http.status_code == 200, negative_http.text
    negative_payload = negative_http.json()
    assert negative_payload["success"] is True, negative_payload
    assert len(negative_payload["result_data"]) == 2
    assert all(item["is_complex"] for item in negative_payload["result_data"])
