"""Algebra114 AS-FAC-04 original difference of cubes factorization via HTTP."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

def test_as_fac_04_difference_of_cubes_http():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-FAC-04 | N2 |" in source
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": "x**3-1"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    x = sp.symbols("x")
    factored = sp.sympify(result["result_text"])
    assert sp.simplify(factored - (x-1)*(x*x+x+1)) == 0
    assert len(sp.factor_list(factored)[1]) == 2
