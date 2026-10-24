"""SY-V-16: finite sum HTTP evaluation, inclusive bounds and real output reentry."""
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


def test_syv16_finite_sum_exact_http_and_reentry():
    row = ROWS["SY-V-16"]
    assert row["entrada"] == r"\sum_{k=1}^{10}k"
    assert row["operacion"] == "valor" and row["esperado"] == "55"
    # The independent frontend test converts the original source to this whole expression.
    expression = "sum(k,k,1,10)"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True and data["operation"] == "evaluate", data
        assert data["result_type"] == "scalar", data
        assert data["input_text"] == expression and data["request_id"], data
        assert data["result_text"] == "55" and data["result_latex"] == "55", data
        assert data["result_approx"] == 55, data
        assert data["error_code"] is None and data["error_message"] is None, data
        repeated = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert repeated.status_code == 200, repeated.text
        again = repeated.json()
        MathResponse.model_validate(again)
        assert again["success"] is True, again
        assert again["request_id"] != data["request_id"], again
        assert again["result_text"] == "55" and again["result_latex"] == "55", again
        assert again["result_approx"] == 55 and again["error_code"] is None, again
        for source, expected in [("sum(k,k,2,10)", "54"), ("sum(k,k,1,9)", "45")]:
            control = client.post("/api/v1/evaluate", json={"expression": source})
            assert control.status_code == 200, control.text
            value = control.json()
            MathResponse.model_validate(value)
            assert value["success"] is True and value["result_text"] == expected, value
