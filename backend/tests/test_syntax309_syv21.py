"""SY-V-21: bounded permutation alias, local P priority, HTTP result reentry."""
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


def test_syv21_permutation_alias_declared_and_actual_output_reentry():
    row = ROWS["SY-V-21"]
    assert row["entrada"] == "P(5,2)" and row["esperado"] == "20"
    assert row["operacion"] == "valor" and "función" in row["nota"]
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True and data["operation"] == "evaluate", data
        assert data["result_type"] == "scalar" and data["input_text"] == row["entrada"], data
        assert data["request_id"] and data["result_approx"] == 20, data
        assert data["result_text"] == "20" and data["result_latex"] == "20", data
        assert data["error_code"] is None and data["error_message"] is None, data
        assert any("permutaciones" in w and "nPr" in w for w in data["warnings"]), data
        repeated = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert repeated.status_code == 200, repeated.text
        again = repeated.json()
        MathResponse.model_validate(again)
        assert again["success"] is True and again["result_text"] == "20", again
        assert again["request_id"] != data["request_id"] and again["result_approx"] == 20, again


def test_syv21_local_function_priority_controls_and_alias_domain():
    with TestClient(app) as client:
        for source, expected in [
            ("P(x,y)=x+y;P(5,2)", "7"),
            ("P(x)=x+1;P(5)", "6"),
            ("P(6,2)", "30"), ("P(5,0)", "1"), ("P(5,5)", "120"),
            ("P(5,2)", "20"),
        ]:
            response = client.post("/api/v1/evaluate", json={"expression": source})
            assert response.status_code == 200, response.text
            data = response.json()
            MathResponse.model_validate(data)
            assert data["success"] is True and data["result_text"] == expected, data
            if "=" in source:
                assert not any("permutaciones" in w for w in data["warnings"]), data
        for source in ["P(-1,2)", "P(2,5)", "P(171,2)", "P(5,1/2)"]:
            data = client.post("/api/v1/evaluate", json={"expression": source}).json()
            MathResponse.model_validate(data)
            assert data["success"] is False and data["error_message"], data
        # Explicitly declared P is ambiguous as the alias; do not silently override it.
        conflict = client.post("/api/v1/evaluate", json={
            "expression": "P(5,2)", "substitutions": {"P": "3"}}).json()
        MathResponse.model_validate(conflict)
        assert conflict["success"] is False and conflict["error_code"] == "VALIDATION_ERROR", conflict
