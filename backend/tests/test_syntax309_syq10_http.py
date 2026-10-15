"""SY-Q-10: absolute-value strict inequality via the real public HTTP endpoint."""
import json
import os
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse

_ROWS = {r["id"]: r for r in (json.loads(line) for line in
    (Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl")
    .read_text(encoding="utf-8").splitlines() if line.strip())}

def test_syq10_public_http_open_interval_and_strict_boundaries():
    case = _ROWS["SY-Q-10"]
    assert case["entrada"] == r"\lvert x\rvert<3"
    assert case["esperado"] == r"x\in(-3,3)"
    expected = sp.Interval.open(-3, 3)
    with TestClient(app) as client:
        for expression in (case["entrada"], "abs(x)<3"):
            response = client.post("/api/v1/inequality", json={"inequality": expression})
            assert response.status_code == 200, response.text
            body = MathResponse.model_validate(response.json())
            assert body.success is True, response.text
            assert body.result_text == str(expected), response.text
            assert body.result_latex == sp.latex(expected), response.text
            assert body.request_id
        control = client.post("/api/v1/inequality", json={"inequality": "x<3"})
        assert control.status_code == 200
        ordinary = MathResponse.model_validate(control.json())
        assert ordinary.success and ordinary.result_text == str(sp.Interval.open(-sp.oo, 3))
