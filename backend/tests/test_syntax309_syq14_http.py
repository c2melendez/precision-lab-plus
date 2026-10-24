"""SY-Q-14: preserve exact LaTeX array fixture, test real Plus system API."""
import json
import os
from pathlib import Path
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse

_CASES = {c["id"]: c for c in (json.loads(s) for s in
    (Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl").read_text(encoding="utf-8").splitlines() if s.strip())}

def test_syq14_array_fixture_real_system_endpoint():
    case = _CASES["SY-Q-14"]
    assert case["entrada"] == r"\left\{\begin{array}{l}x+y=3\\ x-y=1\end{array}\right."
    assert case["esperado"] == "(x,y)=(2,1)"
    # Plus endpoint accepts structured equations; this does not claim native
    # frontend acceptance of raw LaTeX array syntax.
    with TestClient(app) as client:
        response = client.post("/api/v1/solve/system", json={
            "equations": ["x+y=3", "x-y=1"], "variables": ["x", "y"]
        })
        assert response.status_code == 200, response.text
        result = MathResponse.model_validate(response.json())
        assert result.success
        assert result.operation.value == "solve_system"
        assert result.result_data and len(result.result_data) == 1
        assert result.result_data[0].text.replace(" ", "") == "x=2,y=1"
        assert result.request_id
