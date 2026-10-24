"""Algebra114 AS-FAC-03 original nonmonic quadratic factorization HTTP."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

def test_as_fac_03_nonmonic_trinomial_http():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-FAC-03 | N2 |" in source
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": "6*x**2-11*x+3"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    x = sp.symbols("x")
    factored = sp.sympify(result["result_text"])
    assert sp.simplify(factored - (3*x-1)*(2*x-3)) == 0
    coefficient, factors = sp.factor_list(factored)
    assert coefficient == 1
    assert len(factors) == 2
