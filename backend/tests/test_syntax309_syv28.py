"""SY-V-28: Greek alpha is one symbolic variable, not a constant or letter product."""
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

def test_syv28_symbolic_greek_alpha_and_reentry():
    row = ROWS["SY-V-28"]
    assert row["entrada"] == r"\alpha+\alpha"
    assert row["esperado"] == r"2\alpha" and row["operacion"] == "valor"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "alpha+alpha"})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert data["result_text"].replace(" ", "") in ("2*alpha", "2alpha"), data
        different = client.post("/api/v1/evaluate", json={"expression": "alpha+beta"})
        assert different.status_code == 200, different.text
        assert different.json()["success"] is True
        assert different.json()["result_text"] != data["result_text"]
        replay = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert replay.status_code == 200, replay.text
        MathResponse.model_validate(replay.json())
        assert replay.json()["success"] is True
        assert replay.json()["result_text"] == data["result_text"]
        assert replay.json()["request_id"] != data["request_id"]
