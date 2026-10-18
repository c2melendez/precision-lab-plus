"""Algebra114 AS-EXP-09 trinomial square: original six-term oracle via HTTP."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

def test_as_exp_09_trinomial_square_http():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-EXP-09 | N3 |" in source
    with TestClient(app) as client:
        response = client.post("/api/v1/expand", json={"expression": "(a+b+c)**2"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    a,b,c = sp.symbols("a b c")
    expected = a**2+b**2+c**2+2*a*b+2*a*c+2*b*c
    assert sp.simplify(sp.sympify(result["result_text"]) - expected) == 0
