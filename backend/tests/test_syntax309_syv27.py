"""SY-V-27: the ASCII word pi is a reserved mathematical constant in Plus."""
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

def test_syv27_ascii_pi_constant_and_explicit_product():
    row = ROWS["SY-V-27"]
    assert row["entrada"] == "pi" and row["operacion"] == "convencion"
    assert "declarar" in row["nota"]
    with TestClient(app) as client:
        constant = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        explicit = client.post("/api/v1/evaluate", json={"expression": "p*i"})
        latex = client.post("/api/v1/evaluate", json={"expression": "pi"})
        for response in (constant, explicit, latex):
            assert response.status_code == 200, response.text
            MathResponse.model_validate(response.json())
            assert response.json()["success"] is True, response.text
        assert "pi" in constant.json()["result_text"], constant.json()
        assert constant.json()["result_text"] != explicit.json()["result_text"], explicit.json()
        assert constant.json()["result_text"] == latex.json()["result_text"]
        replay = client.post("/api/v1/evaluate", json={"expression": constant.json()["result_text"]})
        assert replay.status_code == 200, replay.text
        MathResponse.model_validate(replay.json())
        assert replay.json()["success"] is True
        assert replay.json()["result_text"] == constant.json()["result_text"]
        assert replay.json()["request_id"] != constant.json()["request_id"]
