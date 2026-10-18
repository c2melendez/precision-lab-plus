"""Algebra114 AS-EXP-06 original two-variable binomial cube through HTTP."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

def test_as_exp_06_two_variable_binomial_cube_http():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-EXP-06 | N2 |" in source
    with TestClient(app) as client:
        response = client.post("/api/v1/expand", json={"expression": "(x+y)**3"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    x,y = sp.symbols("x y")
    assert sp.simplify(sp.sympify(result["result_text"]) - (x**3+3*x**2*y+3*x*y**2+y**3)) == 0
