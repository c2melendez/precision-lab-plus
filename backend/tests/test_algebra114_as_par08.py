"""AS-PAR-08: |x-a| = b over R, with the contract's negative/zero/positive branches."""

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


def test_as_par_08_original_absolute_value_equation_service_and_http():
    source = (
        Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md"
    ).read_text()
    assert "| AS-PAR-08 | N3 |" in source

    x = sympy.symbols("x")

    # b = 0: one unique root x = a.
    for offset in (0, 5):
        equation = f"abs(x-({offset}))=0"
        result = solve_equation(equation, "x")
        roots = _roots(result)
        assert len(roots) == 1
        assert sympy.simplify(roots[0] - offset) == 0
        assert sympy.Abs(roots[0] - offset) == 0

        response = _solve_http(equation)
        assert response.status_code == 200, response.text
        payload = response.json()
        assert payload["success"] is True, payload
        http_roots = _http_roots(payload)
        assert len(http_roots) == 1
        assert sympy.simplify(http_roots[0] - offset) == 0
        assert payload["result_type"] == "equation_solutions"

    # b > 0: exactly two roots x = a +/- b.
    for offset, radius in ((5, 2), (0, 3)):
        equation = f"abs(x-({offset}))={radius}"
        expected = {sympy.Integer(offset + radius), sympy.Integer(offset - radius)}
        result = solve_equation(equation, "x")
        roots = {sympy.simplify(root) for root in _roots(result)}
        assert roots == expected
        assert all(sympy.simplify(sympy.Abs(root - offset) - radius) == 0 for root in roots)

        response = _solve_http(equation)
        assert response.status_code == 200, response.text
        payload = response.json()
        assert payload["success"] is True, payload
        http_roots = {sympy.simplify(root) for root in _http_roots(payload)}
        assert http_roots == expected
        assert payload["result_type"] == "equation_solutions"

    # b < 0: independent real-domain oracle is empty. Do not create roots
    # by mechanically splitting the absolute value into two equations.
    for offset, radius in ((5, -1), (2, -2)):
        equation = f"abs(x-({offset}))=({radius})"
        oracle = sympy.solveset(
            sympy.Abs(x - offset) - radius, x, domain=sympy.S.Reals
        )
        assert oracle == sympy.EmptySet
        result = solve_equation(equation, "x")
        assert result.solutions == []

        response = _solve_http(equation)
        assert response.status_code == 200, response.text
        payload = response.json()
        assert payload["success"] is True, payload
        assert payload["result_type"] == "equation_solutions"
        assert payload["result_data"] == []
