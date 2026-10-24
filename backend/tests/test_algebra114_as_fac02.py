"""Algebra114 AS-FAC-02: original factorization by HTTP."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

def test_as_fac_02_quadratic_trinomial_http():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-FAC-02 | N1 |" in source
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": "x**2+5*x+6"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    x = sp.symbols("x")
    factored = sp.sympify(result["result_text"])
    assert sp.simplify(factored - (x+2)*(x+3)) == 0
    assert sorted([str(root) for root in sp.solve(factored, x)]) == ["-2", "-3"]
