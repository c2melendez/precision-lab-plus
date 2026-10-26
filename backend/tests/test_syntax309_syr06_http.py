"""SY-R-06 converter witnesses: natural versus decimal logarithm, finite approximation and reentry."""
import os
import math
import pytest
import sympy as sp
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse

@pytest.mark.parametrize("witness, exact", [("ln(2)", sp.log(2)), ("ln(3)", sp.log(3)), ("log(2)", sp.log(2, 10))])
def test_syr06_logarithm_exact_mathresponse_numeric_value_and_reentry(witness, exact):
    expected = float(exact)
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": witness, "angle_unit": "rad"})
        assert response.status_code == 200, response.text
        result = MathResponse.model_validate(response.json())
        assert result.success and result.result_type.value == "scalar", result
        actual = sp.sympify(result.result_text)
        assert sp.simplify(actual - exact) == 0 and not actual.has(sp.Float), result
        assert result.result_approx is not None and math.isfinite(result.result_approx), result
        assert abs(result.result_approx - expected) <= 1e-9 * abs(expected), result
        if witness == "ln(2)":
            assert abs(result.result_approx - 0.6931471806) <= 1e-9 * 0.6931471806, result
        again = client.post("/api/v1/evaluate", json={"expression": result.result_text, "angle_unit": "rad"})
        assert again.status_code == 200, again.text
        restored = MathResponse.model_validate(again.json())
        assert restored.success and sp.simplify(sp.sympify(restored.result_text) - exact) == 0, restored
        assert restored.result_approx is not None and math.isfinite(restored.result_approx), restored
        assert abs(restored.result_approx - expected) <= 1e-9 * abs(expected), restored
