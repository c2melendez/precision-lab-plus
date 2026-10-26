"""AS-DIV-02: original cubic division, exact quotient/remainder and HTTP."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.algebra_service import simplify_expression


def test_as_div_02_original_cubic_division_service_http():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-DIV-02 | N2 |" in source
    x = sp.Symbol("x")
    numerator, denominator = x**3-8, x-2
    expected = x**2+2*x+4
    quotient, remainder = sp.div(numerator, denominator, x)
    assert sp.expand(quotient-expected) == 0
    assert remainder == 0
    assert sp.expand(numerator-denominator*quotient-remainder) == 0
    assert denominator.subs(x, 2) == 0
    service = simplify_expression("(x**3-8)/(x-2)")
    assert sp.simplify(service.result_expr-expected) == 0
    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": "(x**3-8)/(x-2)"})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    assert sp.simplify(sp.sympify(payload["result_text"])-expected) == 0
