"""SY-R-12 rejects the raw prose fixture over HTTP and recovers in the same client."""
import os
from fastapi.testclient import TestClient

os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse


def test_syr12_nonmathematical_text_rejection_and_recovery():
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": r"\text{no existe}"})
        assert response.status_code == 200, response.text
        rejected = MathResponse.model_validate(response.json())
        assert not rejected.success, rejected
        assert rejected.error_code.value == "PARSE_ERROR", rejected
        assert "Texto no matemático" in rejected.error_message, rejected

        response = client.post("/api/v1/evaluate", json={"expression": "2+3"})
        assert response.status_code == 200, response.text
        recovered = MathResponse.model_validate(response.json())
        assert recovered.success, recovered
        assert recovered.result_text == "5", recovered
