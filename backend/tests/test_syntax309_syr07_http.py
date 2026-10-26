"""SY-R-07: finite nonzero small value, strict relative tolerance and result reentry."""
import os
import math
import pytest
import sympy as sp
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse

@pytest.mark.parametrize("witness, expected", [
    ("1.5*10^(-7)", 0.00000015),
    ("2.5*10^(-6)", 0.0000025),
    ("-1.5*10^(-7)", -0.00000015),
    ("3/20000000", 0.00000015),
])
def test_syr07_scientific_small_value_and_reentry(witness, expected):
    def check(result):
        assert result.success and result.result_type.value == "scalar", result
        text_value = sp.sympify(result.result_text)
        assert not text_value.free_symbols and text_value.is_real is True, result
        value = float(text_value)
        assert math.isfinite(value) and value != 0, result
        assert abs(value - expected) <= 1e-9 * abs(expected), result
        assert result.result_approx is not None and math.isfinite(result.result_approx) and result.result_approx != 0, result
        assert abs(result.result_approx - expected) <= 1e-9 * abs(expected), result
        return text_value
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": witness, "angle_unit": "rad"})
        assert response.status_code == 200, response.text
        result = MathResponse.model_validate(response.json())
        original = check(result)
        if witness == "3/20000000":
            assert original == sp.Rational(3, 20000000) and not original.has(sp.Float), result
        again = client.post("/api/v1/evaluate", json={"expression": result.result_text, "angle_unit": "rad"})
        assert again.status_code == 200, again.text
        restored = MathResponse.model_validate(again.json())
        check(restored)
