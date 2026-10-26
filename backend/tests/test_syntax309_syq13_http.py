"""SY-Q-13: semicolon-delimited source adapted to the public system endpoint."""
import json
import os
from pathlib import Path

from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse

_ROWS = {row["id"]: row for row in (json.loads(line) for line in
    (Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl")
    .read_text(encoding="utf-8").splitlines() if line.strip())}

def test_syq13_semicolon_system_api_exact_solution():
    fixture = _ROWS["SY-Q-13"]
    assert fixture["entrada"] == r"x+y=3;\ x-y=1"
    assert fixture["esperado"] == "(x,y)=(2,1)"
    parts = [part.strip().removeprefix(r"\ ").strip() for part in fixture["entrada"].split(";")]
    assert parts == ["x+y=3", "x-y=1"]
    with TestClient(app) as client:
        reply = client.post("/api/v1/solve/system", json={
            "equations": parts, "variables": ["x", "y"]
        })
        assert reply.status_code == 200, reply.text
        body = MathResponse.model_validate(reply.json())
        assert body.success
        assert body.operation.value == "solve_system"
        assert body.request_id
        assert body.result_data is not None and len(body.result_data) == 1
        assert body.result_data[0].text.replace(" ", "") == "x=2,y=1"
