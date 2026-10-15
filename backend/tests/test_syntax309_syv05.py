"""SY-V-05: symbolic argument substitution in a local function definition."""
import json
import os
from pathlib import Path

os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
import sympy
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.responses import MathResponse

ROWS = {x["id"]: x for x in (json.loads(s) for s in (Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl").read_text(encoding="utf-8").splitlines() if s.strip())}

def test_syv05_symbolic_function_call_and_reentry():
    row = ROWS["SY-V-05"]
    assert row["entrada"] == r"f(x)=x^{2};\ f(x+1)"
    assert row["operacion"] == "equivalente"
    assert row["esperado"] == "(x+1)^{2}"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        x = sympy.Symbol("x")
        expression = sympy.sympify(data["result_text"])
        assert expression.free_symbols == {x}, data
        assert sympy.simplify(expression - (x+1)**2) == 0, data
        reentry = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert reentry.status_code == 200, reentry.text
        repeated = reentry.json()
        MathResponse.model_validate(repeated)
        assert repeated["success"] is True, repeated
        assert sympy.simplify(sympy.sympify(repeated["result_text"]) - (x+1)**2) == 0, repeated
