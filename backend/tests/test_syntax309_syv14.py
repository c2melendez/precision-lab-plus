"""SY-V-14: right reciprocal limit, direction controls, infinity reuse."""
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


def test_syv14_positive_infinity_right_limit_and_reuse_as_limit_point():
    row = ROWS["SY-V-14"]
    assert row["entrada"] == r"\lim_{x\to0^{+}}\frac{1}{x}"
    assert row["operacion"] == "valor" and row["esperado"] == r"+\infty"
    # The frontend separately extracts the original LaTeX into this payload.
    payload = {"expression": "1/x", "variable": "x", "point": "0", "direction": "right"}
    with TestClient(app) as client:
        response = client.post("/api/v1/limit", json=payload)
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True and data["operation"] == "limit", data
        assert data["result_type"] == "scalar" and data["request_id"], data
        assert data["result_text"] == "oo" and data["result_latex"] == r"\infty", data
        assert data["result_approx"] is None, data
        assert data["error_code"] is None and data["error_message"] is None, data
        # Infinity is not a finite /evaluate number. Reuse actual output as a limit point.
        repeated = client.post("/api/v1/limit", json={**payload, "point": data["result_text"], "direction": "both"})
        assert repeated.status_code == 200, repeated.text
        again = repeated.json()
        MathResponse.model_validate(again)
        assert again["success"] is True and again["result_text"] == "0", again
        assert again["request_id"] != data["request_id"], again
        # Discriminating controls: changing side must change semantics.
        left = client.post("/api/v1/limit", json={**payload, "direction": "left"}).json()
        both = client.post("/api/v1/limit", json={**payload, "direction": "both"}).json()
        MathResponse.model_validate(left)
        MathResponse.model_validate(both)
        assert left["success"] is True and left["result_text"] == "-oo", left
        assert both["success"] is True and both["result_text"] == "DNE", both
