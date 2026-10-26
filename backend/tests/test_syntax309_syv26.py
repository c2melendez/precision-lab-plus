"""SY-V-26: bare sinx is ambiguous; document actual symbolic API convention."""
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

def test_syv26_bare_sinx_not_silently_function_call():
    row = ROWS["SY-V-26"]
    assert row["entrada"] == "sinx" and row["operacion"] == "convencion"
    assert "función" in row["nota"]
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "sinx"})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True and "sinx" in data["result_text"], data
        explicit = client.post("/api/v1/evaluate", json={"expression": "sin(x)"}).json()
        MathResponse.model_validate(explicit)
        assert explicit["success"] is True and data["result_text"] != explicit["result_text"], (data, explicit)

def test_syv26_bare_sinx_reentry_preserves_symbol():
    with TestClient(app) as client:
        first = client.post("/api/v1/evaluate", json={"expression": "sinx"}).json()
        assert first["success"] is True, first
        replay = client.post("/api/v1/evaluate", json={"expression": first["result_text"]}).json()
        MathResponse.model_validate(replay)
        assert replay["success"] is True and replay["result_text"] == first["result_text"], replay
        assert replay["request_id"] != first["request_id"], replay
