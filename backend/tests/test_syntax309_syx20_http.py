"""SY-X-20: preserve the original Unicode fixture and reject invalid input over HTTP."""
import json
import os
from pathlib import Path

os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from fastapi.testclient import TestClient
from app.main import app


def test_syx20_unicode_invalid_character_http_rejection_and_reentry():
    fixture_path = Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl"
    row = next(
        json.loads(line)
        for line in fixture_path.read_text(encoding="utf-8").splitlines()
        if json.loads(line)["id"] == "SY-X-20"
    )
    source = row["entrada"]
    assert source == "\U0001f600+1"
    assert [ord(char) for char in source] == [0x1F600, 0x2B, 0x31]
    assert row["esperado"] == "error claro de carácter no válido"

    request_ids = []
    with TestClient(app) as client:
        rejected = client.post("/api/v1/evaluate", json={"expression": source})
        assert rejected.status_code in (200, 422), rejected.text
        assert rejected.headers["content-type"].startswith("application/json")
        body = rejected.json()
        assert body["success"] is False, body
        assert body["error_code"] in ("PARSE_ERROR", "VALIDATION_ERROR"), body
        assert body["result_text"] is None and body["result_latex"] is None, body
        assert isinstance(body["error_message"], str) and body["error_message"].strip(), body
        assert body["request_id"], body
        request_ids.append(body["request_id"])

        for expression in ("2+3", "5"):
            recovered = client.post("/api/v1/evaluate", json={"expression": expression})
            assert recovered.status_code == 200, recovered.text
            result = recovered.json()
            assert result["success"] is True and result["result_text"] == "5", result
            assert result["request_id"], result
            request_ids.append(result["request_id"])

    assert len(set(request_ids)) == 3
