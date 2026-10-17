"""SY-X-07: reject actual infinity subtraction, never a false finite result."""
import json
import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app

@pytest.mark.parametrize("source", [r"\infty-\infty", "oo-oo", "∞-∞", "(oo)-(oo)", "(-oo)-(-oo)"])
def test_syx07_indeterminate_rejection_and_real_http_recovery(source):
    row = next(json.loads(line) for line in (Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl").read_text().splitlines() if json.loads(line)["id"] == "SY-X-07")
    assert row["entrada"] == r"\infty-\infty"
    assert row["esperado"] == "indeterminado: error claro"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": source})
        assert response.status_code == 200, response.text
        body = response.json()
        assert not body["success"] and body["error_code"] == "DOMAIN_ERROR", body
        assert "indeterminad" in body["error_message"].lower(), body
        assert body.get("result_text") is None and body.get("result_latex") is None
        ids = [body["request_id"]]
        expression = "2+3"
        for _ in range(2):
            response = client.post("/api/v1/evaluate", json={"expression": expression})
            assert response.status_code == 200
            body = response.json()
            assert body["success"] and body["result_text"] == body["result_latex"] == "5", body
            assert body["request_id"] not in ids
            ids.append(body["request_id"])
            expression = body["result_latex"]

@pytest.mark.parametrize("source,expected", [("3-3", "0"), ("3-2", "1")])
def test_syx07_finite_subtraction_controls(source, expected):
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": source})
        assert response.status_code == 200
        body = response.json()
        assert body["success"] and body["result_text"] == expected, body
