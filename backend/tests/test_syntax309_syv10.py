"""SY-V-10 indefinite integral with attached xdx differential."""
import json
import os
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse
ROWS = {v["id"]: v for v in (json.loads(line) for line in (Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl").read_text(encoding="utf-8").splitlines() if line.strip())}

def test_syv10_attached_differential_http_roundtrip():
    row = ROWS["SY-V-10"]
    assert row["entrada"] == r"\int xdx"
    assert row["operacion"] == "equivalente"
    assert row["esperado"] == r"\frac{x^{2}}{2}+C"
    x, C = sp.symbols("x C")
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        actual = sp.sympify(data["result_text"].replace("^", "**"), locals={"x": x, "C": C})
        assert actual.has(C) and sp.simplify(sp.diff(actual, x)-x) == 0, data
        second = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert second.status_code == 200, second.text
        again = second.json()
        MathResponse.model_validate(again)
        assert again["success"] is True, again
        repeated = sp.sympify(again["result_text"].replace("^", "**"), locals={"x": x, "C": C})
        assert repeated.has(C) and sp.simplify(sp.diff(repeated, x)-x) == 0, again
