"""Original Algebra114 AS-SIM-04 product-power HTTP oracle."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

def test_as_sim_04_http():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-SIM-04 | N1 | \\((xy)^{3}\\) | \\(x^{3}y^{3}\\) |" in source
    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": "(x*y)**3"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True, data
    x, y = sp.symbols("x y")
    assert sp.simplify(sp.sympify(data["result_text"]) - x**3*y**3) == 0
