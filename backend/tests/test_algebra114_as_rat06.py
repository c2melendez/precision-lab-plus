"""AS-RAT-06 original difference quotient, conjugate and domain."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.algebra_service import simplify_expression


def test_as_rat_06_variable_radical_quotient_service_http():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-RAT-06 | N2 |" in source
    x, h = sp.symbols("x h")
    original = "(sqrt(x+h)-sqrt(x))/h"
    expected = 1/(sp.sqrt(x+h)+sp.sqrt(x))
    service = simplify_expression(original)
    for xx, hh in [(1, 1), (4, 0.5), (9, -2), (0.25, 2)]:
        assert xx > 0 and hh > -xx and hh != 0
        actual = sp.N(service.result_expr.subs({"x": xx, "h": hh}))
        target = sp.N(expected.subs({x: xx, h: hh}))
        assert abs(float(actual-target)) < 1e-9
    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": original})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    actual = sp.sympify(payload["result_text"])
    assert sp.simplify(actual-expected) == 0
