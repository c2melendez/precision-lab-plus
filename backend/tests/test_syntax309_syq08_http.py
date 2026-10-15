"""SY-Q-08: chained inequality via the real public Plus HTTP route."""
import json
import os
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse

ROWS = {row["id"]: row for row in (json.loads(line) for line in (
    Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl"
).read_text(encoding="utf-8").splitlines() if line.strip())}

def test_syq08_chained_inequality_open_closed_boundaries():
    row = ROWS["SY-Q-08"]
    assert row["entrada"] == r"1<x\le3"
    assert row["esperado"] == r"x\in(1,3]"
    assert row["operacion"] == "resolver"
    expected = sp.Interval.Lopen(1, 3)
    with TestClient(app) as client:
        for expr in ("1<x<=3",):
            reply = client.post("/api/v1/inequality", json={"inequality": expr, "variable": "x"})
            assert reply.status_code == 200, reply.text
            body = MathResponse.model_validate(reply.json())
            assert body.success is True, reply.text
            assert body.operation.value == "inequality"
            assert body.result_text == str(expected)
            assert body.result_latex == sp.latex(expected)
            assert body.has_detailed_steps is False
