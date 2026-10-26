"""X08: existing general evaluator uses the principal complex branch."""
import json
import os
from pathlib import Path
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.responses import MathResponse

def test_original_negative_root_complex_exactness_and_reentry():
    rows = [json.loads(line) for line in (Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl").read_text().splitlines()]
    row = next(row for row in rows if row["id"] == "SY-X-08")
    assert row["entrada"] == r"\sqrt{-1}"
    assert row["esperado"] == "en ℝ: error claro; en ℂ: `i`"
    ids = []
    with TestClient(app) as client:
        def check(source, expected):
            response = client.post("/api/v1/evaluate", json={"expression": source})
            assert response.status_code == 200, response.text
            body = response.json()
            MathResponse.model_validate(body)
            assert body["success"] and body["result_type"] == "scalar", body
            actual = sp.sympify(body["result_text"], locals={"i": sp.I, "I": sp.I})
            assert actual == expected and not actual.free_symbols and not actual.has(sp.Float), body
            assert body["result_approx"] == (float(expected) if expected.is_real else None), body
            assert body["result_latex"] and body["error_code"] is None, body
            ids.append(body["request_id"])
            return body["result_text"]
        check(check("sqrt(-1)", sp.I), sp.I)
        check("sqrt(-4)", 2*sp.I)
        check("i^2", sp.Integer(-1))
        check(check("2+3", sp.Integer(5)), sp.Integer(5))
    assert len(set(ids)) == 6
