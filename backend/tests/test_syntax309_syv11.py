"""Syntax309 SY-V-11: exact bounded integral and HTTP result reentry."""
import json
import os
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse
ROWS = {v["id"]: v for v in (json.loads(line) for line in (Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl").read_text(encoding="utf-8").splitlines() if line.strip())}

def test_syv11_definite_integral_http_exact_and_reentry():
    row = ROWS["SY-V-11"]
    assert row["entrada"] == r"\int_{0}^{1}x\,dx"
    assert row["operacion"] == "valor"
    assert row["esperado"] == r"\frac{1}{2}"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert sp.simplify(sp.sympify(data["result_text"].replace("^", "**"))-sp.Rational(1,2)) == 0, data
        assert data["result_approx"] == 0.5 and data["error_code"] is None, data
        repeated = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert repeated.status_code == 200, repeated.text
        again = repeated.json()
        MathResponse.model_validate(again)
        assert again["success"] is True, again
        assert sp.simplify(sp.sympify(again["result_text"].replace("^", "**"))-sp.Rational(1,2)) == 0, again


def test_syv12_indefinite_integral_dy_treats_x_constant_and_reenters():
    row = ROWS["SY-V-12"]
    assert row["entrada"] == r"\int x\,dy"
    assert row["operacion"] == "equivalente"
    assert row["esperado"] == "xy+C"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert data["error_code"] is None, data
        y = sp.Symbol("y")
        x = sp.Symbol("x")
        parsed = sp.sympify(data["result_text"].replace("^", "**"))
        assert sp.simplify(sp.diff(parsed, y) - x) == 0, data
        assert "C" in data["result_text"], data
        repeated = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert repeated.status_code == 200, repeated.text
        again = repeated.json()
        MathResponse.model_validate(again)
        assert again["success"] is True, again
        returned = sp.sympify(again["result_text"].replace("^", "**"))
        assert sp.simplify(sp.diff(returned, y) - x) == 0, again
        assert "C" in again["result_text"], again
