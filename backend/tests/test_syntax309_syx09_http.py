"""SY-X-09 bounded real HTTP rejection and finite request recovery."""
import json
import os
from pathlib import Path

os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.responses import MathResponse


def test_original_extreme_power_rejected_by_real_http_and_recovery():
    rows = (Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl").read_text().splitlines()
    case = next(json.loads(line) for line in rows if json.loads(line)["id"] == "SY-X-09")
    assert case["entrada"] == "99999999999^{99999999999}"
    assert case["esperado"] == "límite de tiempo o memoria anunciado; nunca bloqueo ni valor falso"

    with TestClient(app) as client:
        ids = []
        for source, success, expected in [
            ("99999999999^99999999999", False, None),
            ("2+3", True, "5"),
            ("5", True, "5"),
        ]:
            response = client.post("/api/v1/evaluate", json={"expression": source})
            assert response.status_code == 200, response.text
            body = response.json()
            MathResponse.model_validate(body)
            assert body["success"] is success, body
            assert body["request_id"] not in ids
            ids.append(body["request_id"])
            if success:
                assert body["result_text"] == expected and body["result_latex"] == expected, body
                assert body["error_code"] is None
            else:
                assert body["error_code"] == "COMPLEXITY_LIMIT", body
                assert body["result_text"] is None and body["result_latex"] is None
                assert "exponente" in body["error_message"].lower(), body
    assert len(ids) == 3
