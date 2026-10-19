"""AS-PAR-06: sqrt(x) = a over R, nonnegative branch and no negative-parameter roots."""

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


def test_as_par_06_original_square_root_equation_service_and_http():
    source = (
        Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md"
    ).read_text()
    assert "| AS-PAR-06 | N3 |" in source

    x, a = sympy.symbols("x a")

    # For the symbolic nonnegative branch, the candidate x=a^2 satisfies
    # sqrt(x)=a under the required condition a>=0.
    assert sympy.simplify(sympy.sqrt(a**2) - a).subs(a, 3) == 0

    # a = 0, 2, 3: the real solution is unique and equals a^2.
    for parameter in (0, 2, 3):
        equation = f"sqrt(x)={parameter}"
        result = solve_equation(equation, "x")
        roots = _roots(result)
        assert len(roots) == 1
        assert sympy.simplify(roots[0]) == parameter**2
        assert sympy.simplify(sympy.sqrt(roots[0]) - parameter) == 0
        assert all(root.is_real is True for root in roots)

        response = _solve_http(equation)
        assert response.status_code == 200, response.text
        payload = response.json()
        assert payload["success"] is True, payload
        http_roots = _http_roots(payload)
        assert len(http_roots) == 1
        assert sympy.simplify(http_roots[0]) == parameter**2
        assert sympy.simplify(sympy.sqrt(http_roots[0]) - parameter) == 0
        assert payload["result_type"] == "equation_solutions"

    # For a < 0, the equation has no real solution. The general solver must
    # not return x=a^2, since squaring would introduce an extraneous root.
    for parameter in (-1, -2):
        equation = f"sqrt(x)=({parameter})"
        real_oracle = sympy.solveset(
            sympy.sqrt(x) - parameter, x, domain=sympy.S.Reals
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
