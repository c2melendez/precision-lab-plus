"""SY-X-21: zero-width source must evaluate exactly or reject clearly."""
import json
import os
from pathlib import Path

os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from fastapi.testclient import TestClient
from app.main import app


def test_syx21_zero_width_unicode_acceptance_or_clear_rejection():
    path = Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl"
    row = next(json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
               if json.loads(line)["id"] == "SY-X-21")
    source = row["entrada"]
    assert source == "1\u200b+\u200b2"
    assert [ord(ch) for ch in source] == [49, 0x200B, 43, 0x200B, 50]
    assert row["esperado"] == r"3\ \text{o error claro}"
    with TestClient(app) as client:
        invalid = client.post("/api/v1/evaluate", json={"expression": source})
        assert invalid.status_code in (200, 422), invalid.text
        body = invalid.json()
        assert body["request_id"], body
        if body["success"]:
            assert body["result_text"] == "3", body
            assert body["result_latex"] is not None, body
            assert body["error_code"] is None, body
        else:
            assert body["error_code"] in ("PARSE_ERROR", "VALIDATION_ERROR"), body
            assert isinstance(body["error_message"], str) and body["error_message"].strip(), body
            assert body["result_text"] is None and body["result_latex"] is None, body
        recovered = client.post("/api/v1/evaluate", json={"expression": "2+3"})
        assert recovered.status_code == 200, recovered.text
        response = recovered.json()
        assert response["success"] and response["result_text"] == "5", response
        assert response["request_id"] != body["request_id"], response
