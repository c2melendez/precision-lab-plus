"""SY-S-15 official ln(e) via real HTTP evaluation."""
import os
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse

def test_sys15_exact_and_reentry():
    with TestClient(app) as client:
        for source in ("ln(e)",):
            response = client.post("/api/v1/evaluate", json={"expression": source, "angle_unit": "rad"})
            assert response.status_code == 200, response.text
            result = MathResponse.model_validate(response.json())
            assert result.success, result
            assert result.result_text == "1", result
            assert result.result_latex == "1", result
            assert result.result_approx == 1.0, result
            again = client.post("/api/v1/evaluate", json={"expression": result.result_text, "angle_unit": "rad"})
            assert MathResponse.model_validate(again.json()).result_text == "1"
