"""SY-V-06 official two-variable function call."""
import json
import os
from pathlib import Path
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.responses import MathResponse
ROWS = {v["id"]: v for v in (json.loads(x) for x in (Path(__file__).resolve().parents[2]/"qa/certification/syntax309_cases.jsonl").read_text(encoding="utf-8").splitlines() if x.strip())}

def test_syv06_two_argument_function_definition_http_roundtrip():
    row = ROWS["SY-V-06"]
    assert row["entrada"] == r"g(x,y)=x+y;\ g(2,3)"
    assert row["operacion"] == "valor"
    assert row["esperado"] == "5"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert data["result_text"] == "5", data
        second = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert second.status_code == 200, second.text
        again = second.json()
        MathResponse.model_validate(again)
        assert again["success"] is True and again["result_text"] == "5", again
