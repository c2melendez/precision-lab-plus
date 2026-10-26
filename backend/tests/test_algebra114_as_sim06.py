"""Algebra114 AS-SIM-06: cancellation with original x != 2 domain."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

def test_as_sim_06_http_cancellation_preserves_domain():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-SIM-06 | N2 |" in source
    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": "(x**2-4)/(x**2-4*x+4)"})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    x = sp.symbols("x")
    result = sp.sympify(payload["result_text"])
    assert sp.simplify(result - (x+2)/(x-2)) == 0
    conditions = payload.get("domain_conditions", [])
    assert any(c.get("kind") == "denominator" and c.get("variable") == "x"
               and sp.sympify(c.get("text"), locals={"x":x}).subs(x,2) in (sp.false, False)
               for c in conditions), conditions
