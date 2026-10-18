"""AS-SIM-02: preserve source power-of-a-power oracle over Plus HTTP."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

def test_algebra114_as_sim_02_power_of_power_http():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text(encoding="utf-8")
    assert "| AS-SIM-02 | N1 | \\((x^{2})^{3}\\) | \\(x^{6}\\) |" in source
    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": "(x**2)**3"})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    x = sp.symbols("x", real=True)
    observed = sp.sympify(payload["result_text"], locals={"x": x})
    assert sp.simplify(observed - x**6) == 0
