"""Algebra114 AS-SIM-01 original expression and symbolic oracle over actual HTTP."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

def test_as_sim_01_http_simplification_matches_original_oracle():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text(encoding="utf-8")
    assert "| AS-SIM-01 | N1 | \\(3x+2y-x+5y\\) | \\(2x+7y\\) |" in source
    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": "3*x+2*y-x+5*y"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    x, y = sp.symbols("x y")
    observed = sp.sympify(result["result_text"])
    assert sp.simplify(observed - (2*x+7*y)) == 0
