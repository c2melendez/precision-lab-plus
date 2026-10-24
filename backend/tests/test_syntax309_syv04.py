"""SY-V-04 official function definition/application full HTTP acceptance."""
import json
import os
from pathlib import Path

os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.responses import MathResponse

ROWS = {x["id"]: x for x in (json.loads(s) for s in (Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl").read_text(encoding="utf-8").splitlines() if s.strip())}

def test_syv04_function_definition_application_original_expression():
    row = ROWS["SY-V-04"]
    assert row["entrada"] == r"f(x)=x^{2};\ f(3)"
    assert row["operacion"] == "valor"
    assert row["esperado"] == "9"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert data["result_text"] == "9", data
        again = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert again.status_code == 200
        output = again.json()
        MathResponse.model_validate(output)
        assert output["success"] is True and output["result_text"] == "9", output
