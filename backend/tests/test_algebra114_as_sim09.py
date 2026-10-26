"""Algebra114 AS-SIM-09: quotient -1 with x=1 excluded."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

def test_as_sim_09_opposite_fraction_http():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-SIM-09 | N3 |" in source
    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": "(x-1)/(1-x)"})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    assert sp.simplify(sp.sympify(payload["result_text"]) + 1) == 0
    x = sp.symbols("x")
    conditions = payload.get("domain_conditions", [])
    assert any(c.get("kind") == "denominator" and c.get("variable") == "x"
               and sp.sympify(c["text"], locals={"x": x}).subs(x, 1) in (sp.false, False)
               for c in conditions), conditions
