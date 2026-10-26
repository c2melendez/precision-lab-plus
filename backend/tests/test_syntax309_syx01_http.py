"""SY-X-01: an empty string gets schema validation, never an internal error."""
import os
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse


def test_syx01_empty_schema_rejection_and_same_client_recovery():
    with TestClient(app) as client:
        request_ids = set()
        for _ in range(2):
            response = client.post("/api/v1/evaluate", json={"expression": ""})
            assert response.status_code == 422, response.text
            rejected = MathResponse.model_validate(response.json())
            assert not rejected.success and rejected.operation.value == "evaluate", rejected
            assert rejected.error_code.value == "VALIDATION_ERROR", rejected
            assert rejected.error_message == "El payload enviado no cumple el schema esperado.", rejected
            assert rejected.result_text is None and rejected.result_latex is None, rejected
            assert rejected.request_id and rejected.request_id not in request_ids, rejected
            request_ids.add(rejected.request_id)

            response = client.post("/api/v1/evaluate", json={"expression": "2+3"})
            assert response.status_code == 200, response.text
            recovered = MathResponse.model_validate(response.json())
            assert recovered.success and recovered.result_type.value == "scalar", recovered
            assert recovered.result_text == "5", recovered
            assert recovered.error_code is None and recovered.error_message is None, recovered
            assert recovered.request_id and recovered.request_id not in request_ids, recovered
            request_ids.add(recovered.request_id)
