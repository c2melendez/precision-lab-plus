"""Algebra114 AS-AVS-05: |x|+x by cases over the reals (service + HTTP)."""

from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app
from app.services.algebra_service import simplify_expression

x = sp.Symbol("x")
ORIGINAL = "abs(x)+x"
OFFICIAL = [sp.Integer(0), 2 * x]
CONDITIONS = ["x < 0", "x >= 0"]
POINTS = [-5, -1, -0.5, 0, 0.5, 1, 4]


def _expected(t):
    return 2 * t if t >= 0 else 0


def _assert_official_partition(piecewise):
    assert isinstance(piecewise, sp.Piecewise), piecewise
    assert [piece.expr for piece in piecewise.args] == OFFICIAL
    assert [str(piece.cond) for piece in piecewise.args] == CONDITIONS
    for t in POINTS:
        holders = [piece for piece in piecewise.args if bool(piece.cond.subs(x, t))]
        assert len(holders) == 1, (t, piecewise)
        value = float(holders[0].expr.subs(x, t))
        assert abs(value - (abs(t) + t)) < 1e-12
        assert abs(value - _expected(t)) < 1e-12
    assert sp.piecewise_fold(piecewise).has(sp.Abs) is False


def test_as_avs_05_source_row():
    root = Path(__file__).resolve().parents[2]
    source = (root / "qa/certification/algebra114_source.md").read_text(encoding="utf-8")
    assert (
        "| AS-AVS-05 | N3 | \\(|x|+x\\) | \\(2x\\) si \\(x\\ge0\\); \\(0\\) si \\(x<0\\) |"
    ) in source


def test_as_avs_05_piecewise_service_and_http():
    service = simplify_expression(ORIGINAL)
    _assert_official_partition(service.result_expr)

    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": ORIGINAL})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    assert "Abs" not in payload["result_text"]
    assert "\\begin{cases}" in payload["result_latex"]
    explicit = {"x": x, "Piecewise": lambda *args: sp.Piecewise(*args, evaluate=False)}
    observed = sp.parse_expr(payload["result_text"], local_dict=explicit)
    assert observed == service.result_expr
    _assert_official_partition(observed)
