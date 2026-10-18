"""Algebra114 AS-FAC-06 original cubic factorization via HTTP."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

def test_as_fac_06_three_linear_factors_http():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-FAC-06 | N2 |" in source
    with TestClient(app) as client:
        response = client.post("/api/v1/factor", json={"expression": "x**3-6*x**2+11*x-6"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    x = sp.symbols("x")
    actual = sp.sympify(result["result_text"])
    expected = (x-1)*(x-2)*(x-3)
    assert sp.simplify(actual-expected) == 0
    assert set(sp.factor_list(actual)[1]) == {(x-1, 1), (x-2, 1), (x-3, 1)}
