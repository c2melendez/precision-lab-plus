"""SY-Q-16 official nonlinear two-solution system through Plus public HTTP."""
import json
import os
from pathlib import Path
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse

_CASES = {c["id"]: c for c in (json.loads(s) for s in (Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl").read_text(encoding="utf-8").splitlines() if s.strip())}

def test_syq16_nonlinear_system_all_exact_roots():
    fixture = _CASES["SY-Q-16"]
    assert fixture["entrada"] == r"\begin{cases}x^{2}+y^{2}=25\\ x+y=7\end{cases}"
    assert fixture["esperado"] == r"(x,y)=(3,4),\ (4,3)"
    with TestClient(app) as client:
        reply = client.post("/api/v1/solve/system", json={
            "equations": ["x^2+y^2=25", "x+y=7"], "variables": ["x", "y"]
        })
        assert reply.status_code == 200, reply.text
        result = MathResponse.model_validate(reply.json())
        assert result.success, reply.text
        assert result.operation.value == "solve_system"
        assert result.request_id
        assert result.result_data is not None
        assert {item.text.replace(" ", "") for item in result.result_data} == {"x=3,y=4", "x=4,y=3"}
        assert all(not item.is_complex for item in result.result_data)
