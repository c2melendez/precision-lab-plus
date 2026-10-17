"""SY-X-22: large integer must be exact or rejected before lossy conversion."""
import json
import os
from pathlib import Path

os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from fastapi.testclient import TestClient
from app.main import app


def test_syx22_10000_digit_integer_exact_or_explicit_size_notice():
    contract = Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl"
    row = next(json.loads(line) for line in contract.read_text(encoding="utf-8").splitlines()
               if json.loads(line)["id"] == "SY-X-22")
    assert "10 000" in row["entrada"] and "coma flotante" in row["esperado"]
    digits = "9" * 10000
    expression = digits + "+1"
    assert len(digits) == 10000 and expression.endswith("+1")
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
        assert response.status_code in (200, 413, 422), response.text[:500]
        body = response.json()
        if body.get("success"):
            assert body.get("result_text") == "1" + ("0" * 10000)
            assert body.get("error_code") is None
        else:
            assert body.get("success") is False, body
            assert body.get("result_text") is None, body
            assert body.get("result_latex") is None, body
            assert body.get("error_code") in ("VALIDATION_ERROR", "COMPLEXITY_LIMIT", "PARSE_ERROR"), body
            assert isinstance(body.get("error_message"), str) and body["error_message"].strip(), body
        recovered = client.post("/api/v1/evaluate", json={"expression": "2+3"})
        assert recovered.status_code == 200, recovered.text
        recovery = recovered.json()
        assert recovery["success"] and recovery["result_text"] == "5", recovery
        if body.get("request_id"):
            assert recovery["request_id"] != body["request_id"], recovery
