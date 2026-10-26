"""SY-Q-09: exclude a real point via the public Plus inequality endpoint."""
import json
import os
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient

os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse

ROWS = {row["id"]: row for row in (json.loads(line) for line in
    (Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl")
    .read_text(encoding="utf-8").splitlines() if line.strip())}

def test_syq09_exclusion_real_http():
    row = ROWS["SY-Q-09"]
    assert row["entrada"] == r"x\neq2"
    assert row["esperado"] == r"x\in\mathbb{R}\setminus\{2\}"
    expected = sp.S.Reals - sp.FiniteSet(sp.Integer(2))
    with TestClient(app) as client:
        for expression in (r"x\neq2", "x≠2", "x!=2"):
            reply = client.post("/api/v1/inequality", json={"inequality": expression})
            assert reply.status_code == 200, reply.text
            body = MathResponse.model_validate(reply.json())
            assert body.success is True, reply.text
            assert body.operation.value == "inequality"
            assert body.result_text == str(expected)
            assert body.result_latex == sp.latex(expected)
            assert body.has_detailed_steps is False
        mismatched = client.post("/api/v1/inequality", json={"inequality":"x!=2","variable":"y"})
        assert mismatched.status_code == 200, mismatched.text
        error = MathResponse.model_validate(mismatched.json())
        assert error.success is False
        assert error.error_code.value == "INVALID_VARIABLE"

def test_syq09_existing_ordered_inequalities_remain_functional():
    with TestClient(app) as client:
        reply = client.post("/api/v1/inequality", json={"inequality":"x<2"})
        assert reply.status_code == 200, reply.text
        body = MathResponse.model_validate(reply.json())
        assert body.success is True
        assert body.result_text == str(sp.Interval.open(-sp.oo, 2))
