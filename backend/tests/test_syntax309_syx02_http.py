"""SY-X-02: original escaped spaces, normalized witness and HTTP recovery."""
import os
import pytest
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse


@pytest.mark.parametrize("source", ["\\ " * 4, " \t\n", "\\ "])
def test_syx02_raw_spacing_rejected_as_empty_and_recovers(source):
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": source})
        assert response.status_code == 200, response.text
        rejected = MathResponse.model_validate(response.json())
        assert not rejected.success and rejected.error_code.value == "PARSE_ERROR", rejected
        assert rejected.error_message == "Escriba una expresión antes de calcular.", rejected
        assert rejected.result_text is None and rejected.result_latex is None, rejected
        response = client.post("/api/v1/evaluate", json={"expression": r"2\ +\ 3"})
        assert response.status_code == 200, response.text
        recovered = MathResponse.model_validate(response.json())
        assert recovered.success and recovered.result_text == "5", recovered
        assert recovered.error_code is None and recovered.request_id != rejected.request_id, recovered


def test_syx02_empty_converter_witness_validates_then_recovers():
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": ""})
        assert response.status_code == 422, response.text
        rejected = MathResponse.model_validate(response.json())
        assert not rejected.success and rejected.error_code.value == "VALIDATION_ERROR", rejected
        assert rejected.error_message and rejected.result_text is None, rejected
        response = client.post("/api/v1/evaluate", json={"expression": "2+3"})
        assert response.status_code == 200, response.text
        recovered = MathResponse.model_validate(response.json())
        assert recovered.success and recovered.result_text == "5", recovered
        assert recovered.request_id != rejected.request_id, recovered
