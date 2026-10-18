"""Algebra114 AS-SIM-03: original multiplication of powers over HTTP."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

def test_algebra114_as_sim_03_multiply_powers_http():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text(encoding="utf-8")
    assert "| AS-SIM-03 | N1 | \\(x^{2}x^{3}\\) | \\(x^{5}\\) |" in source
    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": "x**2*x**3"})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    x = sp.symbols("x", real=True)
    assert sp.simplify(sp.sympify(payload["result_text"], locals={"x": x}) - x**5) == 0
