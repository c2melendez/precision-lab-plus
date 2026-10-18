"""AS-SIM-05: cancellable rational expression must retain x != 1."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

def test_algebra114_as_sim_05_http_domain_preservation():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-SIM-05 | N2 | \\(\\frac{x^{2}-1}{x-1}\\) | \\(x+1\\), con \\(x\\neq1\\) |" in source
    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": "(x**2-1)/(x-1)"})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["success"] is True, result
    x = sp.symbols("x")
    assert sp.simplify(sp.sympify(result["result_text"]) - (x + 1)) == 0
    conditions = result.get("domain_conditions", [])
    assert any(c.get("variable") == "x" and c.get("kind") == "denominator"
               and sp.simplify(sp.sympify(c["text"], locals={"x": x}).lhs - x) == 0
               and sp.sympify(c["text"], locals={"x": x}).rhs == 1
               for c in conditions), conditions
