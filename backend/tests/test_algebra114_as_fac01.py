"""Algebra114 AS-FAC-01: original difference of squares via factor HTTP."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

def test_as_fac_01_difference_of_squares_http():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-FAC-01 | N1 |" in source
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": "x**2-9"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    x = sp.symbols("x")
    observed = sp.sympify(result["result_text"])
    assert sp.simplify(observed - (x-3)*(x+3)) == 0
    assert len(sp.factor_list(observed)[1]) == 2
