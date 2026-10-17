"""SY-X-06 accepts explicit length rejection; budgets remain unchanged."""
import json
import os
from pathlib import Path
from unittest.mock import Mock
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.core import exception_handlers


def test_syx06_full10000_characters_readable_length_rejection_and_recovery(monkeypatch):
    logger = Mock()
    monkeypatch.setattr(exception_handlers, "get_logger", lambda: logger)
    rows = (Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl").read_text().splitlines()
    row = next(json.loads(line) for line in rows if json.loads(line)["id"] == "SY-X-06")
    assert row["entrada"] == r"\text{(entrada de 10 000 caracteres)}"
    assert row["esperado"] == "procesada sin bloquear, o rechazada con aviso de longitud"
    source = "1+" * 4999 + "11"
    assert len(source) == 10000
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": source})
        assert response.status_code == 422, response.text
        body = response.json()
        assert not body["success"] and body["error_code"] == "VALIDATION_ERROR", body
        assert body["error_message"] == "Entrada demasiado larga: el máximo permitido es de 500 caracteres.", body
        assert logger.warning.call_count == 1
        warning = logger.warning.call_args.args[0]
        assert "string_too_long" in warning and source not in warning and len(warning) < 250
        assert body.get("result_text") is None and body.get("result_latex") is None
        ids = [body["request_id"]]
        result_source = "2+3"
        for _ in range(2):
            response = client.post("/api/v1/evaluate", json={"expression": result_source})
            assert response.status_code == 200
            body = response.json()
            assert body["success"] and body["result_text"] == body["result_latex"] == "5", body
            assert body["request_id"] and body["request_id"] not in ids
            ids.append(body["request_id"])
            result_source = body["result_latex"]
