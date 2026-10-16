"""SY-R-05 converter witness: exact natural logarithm, finite approximation and reentry."""
import os
import math
import pytest
import sympy as sp
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse

@pytest.mark.parametrize("value", [1, -1, 2])
def test_syr05_asinh_exact_mathresponse_numeric_value_and_reentry(value):
    exact = sp.asinh(value)
    expected = float(exact)
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": f"asinh({value})", "angle_unit": "rad"})
        assert response.status_code == 200, response.text
        result = MathResponse.model_validate(response.json())
        assert result.success and result.result_type.value == "scalar", result
        actual = sp.sympify(result.result_text)
        assert sp.simplify(actual - exact) == 0 and not actual.has(sp.Float), result
        assert result.result_approx is not None and math.isfinite(result.result_approx), result
        assert abs(result.result_approx - expected) <= 1e-9 * abs(expected), result
        if value == 1:
            assert abs(result.result_approx - 0.881373587) <= 1e-9 * 0.881373587, result
        again = client.post("/api/v1/evaluate", json={"expression": result.result_text, "angle_unit": "rad"})
        assert again.status_code == 200, again.text
        restored = MathResponse.model_validate(again.json())
        assert restored.success and sp.simplify(sp.sympify(restored.result_text) - exact) == 0, restored
        assert restored.result_approx is not None and math.isfinite(restored.result_approx), restored
        assert abs(restored.result_approx - expected) <= 1e-9 * abs(expected), restored
