"""SY-V-13: translated limit HTTP contract and actual result reentry.

Original LaTeX intent/conversion is tested separately in the frontend.
"""
import json
import os
from pathlib import Path
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse

ROWS = {v["id"]: v for v in (json.loads(line) for line in
    (Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl")
    .read_text(encoding="utf-8").splitlines() if line.strip())}


def test_syv13_sinc_limit_http_contract_and_output_reentry():
    row = ROWS["SY-V-13"]
    assert row["entrada"] == r"\lim_{x\to0}\frac{\sin x}{x}"
    assert row["operacion"] == "valor"
    assert row["esperado"] == "1"
    # Dedicated endpoint, matching the frontend calculus intent.
    payload = {"expression": "sin(x)/x", "variable": "x", "point": "0", "direction": "both"}
    with TestClient(app) as client:
        response = client.post("/api/v1/limit", json=payload)
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert data["operation"] == "limit" and data["result_type"] == "scalar", data
        assert data["input_text"] == payload["expression"] and data["request_id"], data
        assert data["result_text"] == "1" and data["result_latex"] == "1", data
        assert data["error_code"] is None and data["error_message"] is None, data
        # Reuse the real returned result, rather than submitting the oracle literal.
        repeated = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert repeated.status_code == 200, repeated.text
        again = repeated.json()
        MathResponse.model_validate(again)
        assert again["success"] is True and again["operation"] == "evaluate", again
        assert again["request_id"] != data["request_id"], again
        assert again["result_text"] == "1" and again["result_latex"] == "1", again
        assert again["result_approx"] == 1 and again["error_code"] is None, again
