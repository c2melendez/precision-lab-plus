"""SY-V-22: explicit imaginary i convention; do not invent a variable-mode API."""
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


def test_syv22_imaginary_unit_declared_and_http_reentry():
    row = ROWS["SY-V-22"]
    assert row["entrada"] == "i^{2}" and row["operacion"] == "convencion"
    assert "unidad imaginaria" in row["nota"] and "variable" in row["nota"]
    with TestClient(app) as client:
        # The HTTP API accepts plain expressions; LaTeX source stays in the fixture.
        first = client.post("/api/v1/evaluate", json={"expression": "i^2"})
        assert first.status_code == 200, first.text
        data = first.json()
        MathResponse.model_validate(data)
        assert data["success"] is True and data["result_text"] == "-1", data
        assert data["result_approx"] == -1 and data["error_code"] is None, data
        assert data["request_id"] and data["input_text"] == "i^2", data
        second = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert second.status_code == 200, second.text
        replay = second.json()
        MathResponse.model_validate(replay)
        assert replay["success"] is True and replay["result_text"] == "-1", replay
        assert replay["request_id"] != data["request_id"], replay


def test_syv22_reserved_i_does_not_erase_other_variables():
    with TestClient(app) as client:
        negative_i = client.post("/api/v1/evaluate", json={"expression": "(-i)^2"}).json()
        MathResponse.model_validate(negative_i)
        assert negative_i["success"] is True and negative_i["result_text"] == "-1", negative_i
        x = client.post("/api/v1/evaluate", json={"expression": "x^2"}).json()
        MathResponse.model_validate(x)
        assert x["success"] is True and x["result_text"] != "-1", x
