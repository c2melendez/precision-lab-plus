"""SY-Q-15: aligned LaTeX fixture parsed to real public Plus solve/system payload."""
import json
import os
from pathlib import Path
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse

_ROWS = {v["id"]: v for v in (json.loads(line) for line in
    (Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl").read_text(encoding="utf-8").splitlines() if line.strip())}

def test_syq15_aligned_system_real_http_solution():
    fixture = _ROWS["SY-Q-15"]
    assert fixture["entrada"] == r"\begin{aligned}x+y&=3\\ x-y&=1\end{aligned}"
    assert fixture["esperado"] == "(x,y)=(2,1)"
    # Plus /solve/system expects an equation list; raw MathLive aligned UI is separate.
    source = fixture["entrada"]
    assert source.startswith(r"\begin{aligned}") and source.endswith(r"\end{aligned}")
    content = source[len(r"\begin{aligned}"):-len(r"\end{aligned}")]
    equations = [s.replace("&", "").strip() for s in content.split(r"\\")]
    assert equations == ["x+y=3", "x-y=1"]
    with TestClient(app) as client:
        response = client.post("/api/v1/solve/system", json={"equations": equations, "variables": ["x", "y"]})
        assert response.status_code == 200, response.text
        result = MathResponse.model_validate(response.json())
        assert result.success
        assert result.operation.value == "solve_system"
        assert result.result_data and len(result.result_data) == 1
        assert result.result_data[0].text.replace(" ", "") == "x=2,y=1"
        assert result.request_id
