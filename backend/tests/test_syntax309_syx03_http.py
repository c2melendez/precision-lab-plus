"""SY-X-03 raw row-separator/backslash syntax stays invalid, with recovery."""
import os
import pytest
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse


@pytest.mark.parametrize("source", ["\\" * 2, "\\", "\n" + "\\" * 2 + "\t"])
def test_syx03_literal_backslashes_are_parse_errors_and_recover(source):
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": source})
        assert response.status_code == 200, response.text
        rejected = MathResponse.model_validate(response.json())
        assert not rejected.success and rejected.error_code.value == "PARSE_ERROR", rejected
        assert rejected.result_text is None and rejected.result_latex is None, rejected
        assert rejected.error_message and any(word in rejected.error_message.lower() for word in
            ("sintaxis", "carácter", "comando", "interpretar", "barra")), rejected
        assert rejected.error_message != "Escriba una expresión antes de calcular.", rejected

        response = client.post("/api/v1/evaluate", json={"expression": "2+3"})
        assert response.status_code == 200, response.text
        recovered = MathResponse.model_validate(response.json())
        assert recovered.success and recovered.result_text == "5", recovered
        assert recovered.error_code is None and recovered.request_id != rejected.request_id, recovered
