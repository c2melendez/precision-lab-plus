"""SY-V-23 source conjugate and real HTTP result reentry."""
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

def test_syv23_original_latex_and_reentry():
    row = ROWS["SY-V-23"]
    assert row["entrada"] == r"\overline{3+4i}" and row["operacion"] == "valor"
    with TestClient(app) as client:
        first = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert first.status_code == 200, first.text
        data = first.json()
        MathResponse.model_validate(data)
        assert data["success"] and data["input_text"] == row["entrada"], data
        control = client.post("/api/v1/evaluate", json={"expression": "3-4*i"}).json()
        MathResponse.model_validate(control)
        assert control["success"] and data["result_text"] == control["result_text"], (data, control)
        replay = client.post("/api/v1/evaluate", json={"expression": data["result_text"]}).json()
        MathResponse.model_validate(replay)
        assert replay["success"] and replay["result_text"] == control["result_text"], replay
        assert replay["request_id"] != data["request_id"], replay

def test_syv23_sign_controls():
    with TestClient(app) as client:
        for source, expected in [(r"\overline{3-4i}", "3+4*i"), (r"\overline{-2+5i}", "-2-5*i")]:
            data = client.post("/api/v1/evaluate", json={"expression": source}).json()
            control = client.post("/api/v1/evaluate", json={"expression": expected}).json()
            MathResponse.model_validate(data)
            MathResponse.model_validate(control)
            assert data["success"] and control["success"], (data, control)
            assert data["result_text"] == control["result_text"], (data, control)
