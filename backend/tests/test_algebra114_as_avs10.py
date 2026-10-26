"""Algebra114 AS-AVS-10: |x-1|+|x-5|=c, numeric instances solved by cases over R.

Scope: c<4 (no solution) and c>4 (x = 3 ± c/2) are verified on concrete values.
The c=4 interval [1,5] and the symbolic parameter c are not implemented and must
stay an explicit UNSUPPORTED_OPERATION, never a fabricated finite answer.
"""

from pathlib import Path

import pytest
import sympy as sp
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.responses import ResultType
from app.services.solve_service import solve_equation

x = sp.Symbol("x")


def _post(client, equation):
    response = client.post(
        "/api/v1/solve", json={"equation": equation, "variable": "x", "angle_unit": "rad"}
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_as_avs_10_source_row():
    root = Path(__file__).resolve().parents[2]
    source = (root / "qa/certification/algebra114_source.md").read_text(encoding="utf-8")
    assert (
        "| AS-AVS-10 | N3 | \\(|x-1|+|x-5|=c\\) | Si \\(c<4\\), sin solución; si \\(c=4\\), "
        "\\(x\\in[1,5]\\); si \\(c>4\\), \\(x=3\\pm\\frac{c}{2}\\) |"
    ) in source


@pytest.mark.parametrize("c", [sp.Integer(0), sp.Integer(3), sp.Rational(7, 2)])
def test_as_avs_10_c_below_4_has_no_solution(c):
    equation = f"abs(x-1)+abs(x-5)={c}"
    result = solve_equation(equation, "x")
    assert result.result_type == ResultType.CONTRADICTION
    assert result.solutions == []
    with TestClient(app) as client:
        payload = _post(client, equation)
    assert payload["success"] is True and payload["result_type"] == "contradiction"


@pytest.mark.parametrize("c", [sp.Integer(6), sp.Integer(10), sp.Rational(9, 2)])
def test_as_avs_10_c_above_4_gives_3_plus_minus_c_over_2(c):
    equation = f"abs(x-1)+abs(x-5)={c}"
    expected = sorted([3 - c / 2, 3 + c / 2])
    result = solve_equation(equation, "x")
    assert result.result_type == ResultType.EQUATION_SOLUTIONS
    values = sorted(sp.sympify(s.text) for s in result.solutions)
    assert values == expected
    for value in values:
        assert abs(value - 1) + abs(value - 5) == c
    with TestClient(app) as client:
        payload = _post(client, equation)
    assert sorted(sp.sympify(i["text"]) for i in payload["result_data"]) == expected


@pytest.mark.parametrize("equation", ["abs(x-1)+abs(x-5)=4"])
def test_as_avs_10_interval_case_is_explicitly_unsupported(equation):
    with TestClient(app) as client:
        payload = _post(client, equation)
    assert payload["success"] is False
    assert payload["error_code"] == "UNSUPPORTED_OPERATION"
