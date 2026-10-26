"""SY-V-25: Euler exponential at x=0, explicit HTTP substitution and reentry."""
import json
import os
from pathlib import Path
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse
ROWS = {r["id"]: r for r in (json.loads(line) for line in
    (Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl")
    .read_text(encoding="utf-8").splitlines() if line.strip())}

def test_syv25_euler_explicit_substitution_and_reentry():
    row = ROWS["SY-V-25"]
    assert row["entrada"] == r"\mathrm{e}^{x}\ \text{con}\ x=0"
    assert row["operacion"] == "valor" and row["esperado"] == "1"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "e^x", "substitutions": {"x": "0"}})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True and data["result_text"] == "1", data
        assert data["result_approx"] == 1 and data["request_id"], data
        repeated = client.post("/api/v1/evaluate", json={"expression": data["result_text"]}).json()
        MathResponse.model_validate(repeated)
        assert repeated["success"] is True and repeated["result_text"] == "1", repeated
        assert repeated["request_id"] != data["request_id"], repeated

def test_syv25_x_value_matters():
    with TestClient(app) as client:
        result = client.post("/api/v1/evaluate", json={"expression": "e^x", "substitutions": {"x": "1"}}).json()
        MathResponse.model_validate(result)
        assert result["success"] is True and result["result_text"] != "1", result
