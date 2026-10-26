"""SY-R-03: exact response, official numeric tolerance and text/LaTeX reentry witness."""
import os
import math
import pytest
import sympy as sp
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse

def test_syr03_numeric_value_exact_mathresponse_and_reentry():
    expected = 0.5235987756
    witness = "pi/6"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": witness, "angle_unit": "rad"})
        assert response.status_code == 200, response.text
        result = MathResponse.model_validate(response.json())
        assert result.success, result
        exact = sp.sympify(result.result_text)
        assert sp.simplify(exact - sp.sympify(witness)) == 0 and not exact.has(sp.Float), result
        assert result.result_approx is not None and math.isfinite(result.result_approx), result
        assert abs(result.result_approx - expected) <= 1e-9 * abs(expected), result
        again = client.post("/api/v1/evaluate", json={"expression": result.result_text, "angle_unit": "rad"})
        assert again.status_code == 200, again.text
        restored = MathResponse.model_validate(again.json())
        assert restored.success and sp.simplify(sp.sympify(restored.result_text) - exact) == 0, restored
        assert abs(restored.result_approx - expected) <= 1e-9 * abs(expected), restored
