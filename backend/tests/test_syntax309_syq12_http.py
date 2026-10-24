"""SY-Q-12: comma-separated system source and real Plus HTTP system solver."""
import json
import os
from pathlib import Path

from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse

_CASES = {row["id"]: row for row in (json.loads(line) for line in
    (Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl")
    .read_text(encoding="utf-8").splitlines() if line.strip())}

def test_syq12_comma_source_real_http_system_result():
    row = _CASES["SY-Q-12"]
    assert row["entrada"] == r"x+y=3,\ x-y=1"
    assert row["esperado"] == "(x,y)=(2,1)"
    # Source has exactly one top-level comma, so split into the API equation list.
    parts = [piece.strip().removeprefix(r"\ ").strip() for piece in row["entrada"].split(",")]
    assert parts == ["x+y=3", "x-y=1"]
    with TestClient(app) as client:
        response = client.post("/api/v1/solve/system", json={
            "equations": parts, "variables": ["x", "y"]
        })
        assert response.status_code == 200, response.text
        body = MathResponse.model_validate(response.json())
        assert body.success, response.text
        assert body.operation.value == "solve_system"
        assert body.request_id
        assert body.result_data is not None and len(body.result_data) == 1
        assert body.result_data[0].text.replace(" ", "") == "x=2,y=1"
        assert body.result_data[0].is_complex is False
