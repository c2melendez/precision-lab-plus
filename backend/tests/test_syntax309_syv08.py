"""SY-V-08 official second derivative of x cubed via HTTP and reentry."""
import json
import os
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse
ROWS = {v["id"]: v for v in (json.loads(line) for line in (Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl").read_text(encoding="utf-8").splitlines() if line.strip())}

def test_syv08_second_derivative_original_source_http_roundtrip():
    row = ROWS["SY-V-08"]
    assert row["entrada"] == r"\frac{d^{2}}{dx^{2}}x^{3}"
    assert row["operacion"] == "equivalente"
    assert row["esperado"] == "6x"
    x = sp.Symbol("x")
    expected = 6*x
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        actual = sp.sympify(data["result_text"].replace("^", "**"), locals={"x": x})
        assert sp.simplify(actual - expected) == 0, data
        second = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert second.status_code == 200, second.text
        again = second.json()
        MathResponse.model_validate(again)
        assert again["success"] is True, again
        repeated = sp.sympify(again["result_text"].replace("^", "**"), locals={"x": x})
        assert sp.simplify(repeated - expected) == 0, again
