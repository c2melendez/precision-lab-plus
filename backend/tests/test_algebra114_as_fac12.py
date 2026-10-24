"""Algebra114 AS-FAC-12 original three-variable alternating identity via HTTP."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app


def test_as_fac_12_alternating_three_variable_factorization_http():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-FAC-12 | N3 |" in source
    expression = "x**2*(y-z)+y**2*(z-x)+z**2*(x-y)"
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": expression})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    x, y, z = sp.symbols("x y z")
    actual = sp.sympify(payload["result_text"])
    expected = (x-y)*(x-z)*(y-z)
    assert sp.expand(actual-expected) == 0
    # Check factorization, including the overall sign convention.
    assert sp.factor(actual-expected) == 0
    assert actual.is_Mul and len(actual.free_symbols) == 3
    assert sp.expand(actual.subs({x:1,y:2,z:3})) == -2
