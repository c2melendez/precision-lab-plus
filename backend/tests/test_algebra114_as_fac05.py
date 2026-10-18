"""Algebra114 AS-FAC-05 original sum-of-cubes factorization via HTTP."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

def test_as_fac_05_sum_of_cubes_http():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-FAC-05 | N2 |" in source
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": "x**3+1"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    x = sp.symbols("x")
    factored = sp.sympify(result["result_text"])
    expected = (x+1)*(x*x-x+1)
    assert sp.simplify(factored - expected) == 0
    factors = sp.factor_list(factored)[1]
    assert len(factors) == 2
    assert {(sp.expand(f), exponent) for f, exponent in factors} == {(x+1, 1), (x*x-x+1, 1)}
