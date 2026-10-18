"""Algebra114 AS-EXP-10: retain outer minus during original expansion."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

def test_as_exp_10_negative_product_http():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-EXP-10 | N3 |" in source
    with TestClient(app) as client:
        response = client.post("/api/v1/expand", json={"expression": "-(x-1)*(x+2)"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    x = sp.symbols("x")
    assert sp.simplify(sp.sympify(result["result_text"]) - (-x**2-x+2)) == 0
