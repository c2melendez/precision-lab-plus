"""SY-Q-06/07: exercise the actual public inequality API, not only a SymPy oracle."""
import os
import json
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient

os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse

ROWS = {r["id"]: r for r in (json.loads(line) for line in
    (Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl")
    .read_text(encoding="utf-8").splitlines() if line.strip())}


def test_syq06_q07_real_http_strict_vs_inclusive_endpoints():
    assert ROWS["SY-Q-06"]["entrada"] == r"x^{2}\le4"
    assert ROWS["SY-Q-07"]["entrada"] == r"x^{2}<4"
    with TestClient(app) as client:
        seen = {}
        for name, inequality, expected in (
            ("SY-Q-06", "x^2<=4", sp.Interval(-2, 2)),
            ("SY-Q-07", "x^2<4", sp.Interval.open(-2, 2)),
        ):
            response = client.post("/api/v1/inequality", json={"inequality": inequality, "variable": "x"})
            assert response.status_code == 200, response.text
            body = MathResponse.model_validate(response.json())
            assert body.success is True, response.text
            assert body.operation.value == "inequality"
            assert body.input_text == inequality
            assert body.result_latex == sp.latex(expected), body.result_latex
            assert body.result_text == str(expected), body.result_text
            assert not body.has_detailed_steps
            assert body.error_code is None
            seen[name] = body
        assert seen["SY-Q-06"].request_id != seen["SY-Q-07"].request_id
        assert seen["SY-Q-06"].result_text != seen["SY-Q-07"].result_text


def test_syq06_q07_http_auto_variable_inference_and_reentry():
    with TestClient(app) as client:
        for expression, expected in (("x^2<=4", sp.Interval(-2, 2)), ("x^2<4", sp.Interval.open(-2, 2))):
            response = client.post("/api/v1/inequality", json={"inequality": expression})
            assert response.status_code == 200, response.text
            data = MathResponse.model_validate(response.json())
            assert data.success is True
            assert data.result_text == str(expected)
