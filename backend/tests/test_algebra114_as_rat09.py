"""Algebra114 AS-RAT-09 original symbolic conjugate and domain."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.algebra_service import simplify_expression


def test_as_rat_09_variable_radical_denominator_service_http():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-RAT-09 | N3 |" in source
    x, y = sp.symbols("x y", nonnegative=True)
    original = "1/(sqrt(x)+sqrt(y))"
    expected = (sp.sqrt(x)-sp.sqrt(y))/(x-y)
    service = simplify_expression(original)
    for xx, yy in [(4, 1), (1, 4), (9, 0), (0, 16), (0.25, 2)]:
        assert xx >= 0 and yy >= 0 and xx != yy
        actual = sp.N(service.result_expr.subs({"x": xx, "y": yy}))
        target = sp.N(expected.subs({x: xx, y: yy}))
        assert abs(float(actual-target)) < 1e-9
    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": original})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    actual = sp.sympify(payload["result_text"])
    for xx, yy in [(4, 1), (1, 4), (9, 0), (0, 16), (0.25, 2)]:
        assert abs(float(sp.N(actual.subs({"x": xx, "y": yy}) - expected.subs({x: xx, y: yy})))) < 1e-9
