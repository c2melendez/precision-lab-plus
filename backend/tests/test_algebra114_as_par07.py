"""AS-PAR-07: sqrt(x-a) = b over R, conditional real-domain oracle via service and HTTP."""

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


def test_as_par_07_original_square_root_offset_service_and_http():
    source = (
        Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md"
    ).read_text()
    assert "| AS-PAR-07 | N3 |" in source

    x, a, b = sympy.symbols("x a b")

    # b >= 0: the unique real root is x = a + b**2, and it satisfies
    # the original unsquared equation.
    for offset, parameter in ((5, 0), (5, 2), (0, 3)):
        equation = f"sqrt(x-({offset}))={parameter}"
        result = solve_equation(equation, "x")
        roots = _roots(result)
        assert len(roots) == 1
        expected = sympy.Integer(offset + parameter**2)
        assert sympy.simplify(roots[0] - expected) == 0
        assert sympy.simplify(sympy.sqrt(roots[0] - offset) - parameter) == 0
        assert roots[0].is_real is True

        response = _solve_http(equation)
        assert response.status_code == 200, response.text
        payload = response.json()
        assert payload["success"] is True, payload
        http_roots = _http_roots(payload)
        assert len(http_roots) == 1
        assert sympy.simplify(http_roots[0] - expected) == 0
        assert sympy.simplify(sympy.sqrt(http_roots[0] - offset) - parameter) == 0
        assert payload["result_type"] == "equation_solutions"

    # Symbolically verify the proposed root by substitution. The contract's
    # b >= 0 condition remains necessary because the square root is principal.
    symbolic_root = a + b**2
    assert sympy.simplify(sympy.sqrt(symbolic_root - a) - b).subs(b, 2) == 0

    # b < 0: independent real-domain oracle is empty; squaring must not
    # manufacture the candidate a+b**2.
    for offset, parameter in ((5, -1), (2, -2)):
        equation = f"sqrt(x-({offset}))=({parameter})"
        real_oracle = sympy.solveset(
            sympy.sqrt(x - offset) - parameter, x, domain=sympy.S.Reals
        )
        assert real_oracle == sympy.EmptySet

        result = solve_equation(equation, "x")
        assert result.solutions == []

        response = _solve_http(equation)
        assert response.status_code == 200, response.text
        payload = response.json()
        assert payload["success"] is True, payload
        assert payload["result_type"] == "equation_solutions"
        assert payload["result_data"] == []
