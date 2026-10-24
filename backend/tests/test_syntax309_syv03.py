"""SY-V-03: the pi constant must remain distinct from the symbolic radius."""
import json
import os
from pathlib import Path
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
import sympy
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.responses import MathResponse

DATA = Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl"
ROWS = {r["id"]: r for r in (json.loads(line) for line in DATA.read_text(encoding="utf-8").splitlines() if line.strip())}

def test_syv03_pi_constant_and_r_symbolic_reentry():
    row = ROWS["SY-V-03"]
    assert row["entrada"] == r"\pi r^{2}"
    assert row["operacion"] == "interpretacion"
    assert row["esperado"] == r"\pi\cdot r^{2}"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        r = sympy.Symbol("r")
        expression = sympy.sympify(data["result_text"])
        assert expression.free_symbols == {r}, data
        assert sympy.simplify(expression - sympy.pi*r**2) == 0, data
        again_response = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert again_response.status_code == 200, again_response.text
        again = again_response.json()
        MathResponse.model_validate(again)
        assert again["success"] is True, again
        assert sympy.simplify(sympy.sympify(again["result_text"]) - sympy.pi*r**2) == 0, again
