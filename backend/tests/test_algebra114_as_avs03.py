"""Algebra114 AS-AVS-03: |x-1|+|x+1| by cases over the reals (service + HTTP)."""
from pathlib import Path

import pytest
import sympy as sp
from fastapi.testclient import TestClient

from app.main import app
from app.services.algebra_service import simplify_expression

x = sp.Symbol("x")
OFFICIAL = [-2 * x, sp.Integer(2), 2 * x]
POINTS = [-4, -1.5, -1, -0.25, 0, 0.75, 1, 1.5, 6]


def _expected(t):
    return -2 * t if t < -1 else (2 if t <= 1 else 2 * t)


def _assert_official_partition(piecewise):
    assert isinstance(piecewise, sp.Piecewise), piecewise
    assert [piece.expr for piece in piecewise.args] == OFFICIAL
    for t in POINTS:
        holders = [piece for piece in piecewise.args if bool(piece.cond.subs(x, t))]
        assert len(holders) == 1, (t, piecewise)
        value = float(holders[0].expr.subs(x, t))
        assert abs(value - (abs(t - 1) + abs(t + 1))) < 1e-12
        assert abs(value - _expected(t)) < 1e-12
    assert sp.piecewise_fold(piecewise).has(sp.Abs) is False


def test_as_avs_03_source_row():
    root = Path(__file__).resolve().parents[2]
    source = (root / "qa/certification/algebra114_source.md").read_text(encoding="utf-8")
    assert (
        "| AS-AVS-03 | N2 | \\(|x-1|+|x+1|\\) | \\(-2x\\) si \\(x<-1\\); "
        "\\(2\\) si \\(-1\\le x\\le1\\); \\(2x\\) si \\(x>1\\) |"
    ) in source


def test_as_avs_03_piecewise_service_and_http():
    original = "abs(x-1)+abs(x+1)"
    service = simplify_expression(original)
    _assert_official_partition(service.result_expr)
    assert [str(piece.cond) for piece in service.result_expr.args] == [
        "x < -1",
        "(x >= -1) & (x < 1)",
        "x >= 1",
    ]

    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": original})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    assert "Abs" not in payload["result_text"]
    assert "\\begin{cases}" in payload["result_latex"]
    explicit = {"x": x, "Piecewise": lambda *args: sp.Piecewise(*args, evaluate=False)}
    observed = sp.parse_expr(payload["result_text"], local_dict=explicit)
    assert observed == service.result_expr
    _assert_official_partition(observed)


SCOPED_OUT = ["abs(x)", "3*abs(x)", "abs(x*y)", "abs(x**2-1)", "abs(x)+abs(y)", "sin(abs(x))"]


@pytest.mark.parametrize("expression", SCOPED_OUT)
def test_as_avs_03_rewrite_stays_scoped(expression):
    assert not simplify_expression(expression).result_expr.has(sp.Piecewise)
