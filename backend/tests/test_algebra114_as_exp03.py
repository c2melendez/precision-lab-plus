"""Algebra114 AS-EXP-03 original binomial multiplication via HTTP expand."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

def test_as_exp_03_binomial_product_http():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-EXP-03 | N2 |" in source
    with TestClient(app) as client:
        response = client.post("/api/v1/expand", json={"expression": "(2*x-1)*(3*x+4)"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    x = sp.symbols("x")
    assert sp.simplify(sp.sympify(result["result_text"]) - (6*x**2+5*x-4)) == 0
