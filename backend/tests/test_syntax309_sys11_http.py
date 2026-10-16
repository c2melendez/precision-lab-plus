"""SY-S-11 official Spanish 'sen(x) con x=pi/6' HTTP regression."""
import math
import os
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse


def test_sys11_inline_spanish_substitution_http_and_reentry():
    source = r"sen(x)\ \text{con}\ x=\frac{\pi}{6}"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": source, "angle_unit": "rad"})
        assert response.status_code == 200, response.text
        result = MathResponse.model_validate(response.json())
        assert result.success, result
        assert math.isclose(float(result.result_approx), 0.5, rel_tol=0, abs_tol=1e-12)
        assert result.result_text == "1/2", result.result_text
        assert result.result_latex == r"\frac{1}{2}", result.result_latex
        replay = client.post("/api/v1/evaluate", json={"expression": result.result_text, "angle_unit": "rad"})
        restored = MathResponse.model_validate(replay.json())
        assert restored.success, restored
        assert math.isclose(float(restored.result_approx), 0.5, rel_tol=0, abs_tol=1e-12)
