"""Algebra114 AS-SIM-07: sqrt(x**2) must equal Abs(x) over real x."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

def test_as_sim_07_http_real_absolute_value():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-SIM-07 | N2 | \\(\\sqrt{x^{2}}\\) | \\(\\lvert x\\rvert\\) (no \\(x\\)) |" in source
    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": "sqrt(x**2)"})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    x = sp.symbols("x", real=True)
    observed = sp.sympify(payload["result_text"], locals={"x": x})
    for value in [-7, -2, 0, 3, 8]:
        assert sp.simplify(observed.subs(x, value) - abs(value)) == 0
