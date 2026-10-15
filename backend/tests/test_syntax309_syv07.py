"""SY-V-07 official symbolic first derivative and HTTP reentry."""
import json
import os
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse

ROWS = {v["id"]: v for v in (
    json.loads(line) for line in
    (Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl")
    .read_text(encoding="utf-8").splitlines() if line.strip()
)}


def test_syv07_first_derivative_original_source_http_roundtrip():
    row = ROWS["SY-V-07"]
    assert row["entrada"] == r"\frac{d}{dx}x^{2}"
    assert row["operacion"] == "equivalente"
    assert row["esperado"] == "2x"
    x = sp.Symbol("x")
    expected = 2*x
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
