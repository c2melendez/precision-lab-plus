"""Algebra114 AS-SIM-10: retain x!=0, y!=0, x!=y after cancellation."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

def test_as_sim_10_nested_quotient_http():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-SIM-10 | N3 |" in source
    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": "(1/x-1/y)/(x-y)"})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    x, y = sp.symbols("x y")
    assert sp.simplify(sp.sympify(payload["result_text"]) + 1/(x*y)) == 0
    conditions = payload.get("domain_conditions", [])
    restrictions = [sp.sympify(c["text"], locals={"x":x,"y":y}) for c in conditions]
    for substitutions in [{x:0,y:2}, {x:2,y:0}, {x:2,y:2}]:
        assert any(relation.subs(substitutions) in (sp.false,False) for relation in restrictions), (substitutions, conditions)
