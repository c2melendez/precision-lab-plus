"""AS-SIM-08: real sqrt(x^3) identity and nonnegative domain via HTTP."""
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

def test_as_sim_08_http_real_cube_radical_domain():
    source = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text()
    assert "| AS-SIM-08 | N2 |" in source
    with TestClient(app) as client:
        response = client.post("/api/v1/simplify", json={"expression": "sqrt(x**3)"})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    x = sp.symbols("x", real=True)
    observed = sp.sympify(payload["result_text"], locals={"x": x})
    for value in [0, 1, 2, 9, 16]:
        assert sp.simplify(observed.subs(x,value) - value * sp.sqrt(value)) == 0
    conditions = payload.get("domain_conditions", [])
    assert conditions, payload
    assert any(c.get("variable") == "x" and c.get("kind") in ("even_root",)
               and sp.sympify(c["text"], locals={"x":x}).subs(x,-1) in (sp.false, False)
               and sp.sympify(c["text"], locals={"x":x}).subs(x,0) in (sp.true, True)
               for c in conditions), conditions
