"""SY-S-20: frontend degree-translation witness through real HTTP, rad/deg."""
import os
import pytest
import sympy as sp
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse

@pytest.mark.parametrize("angle_unit", ["rad", "deg"])
def test_sys20_explicit_degree_http_and_reentry(angle_unit):
    # Original fixture: sen(30°). The frontend contract translates ° to
    # an explicit pi/180 factor; the API accepts backend syntax, not LaTeX.
    expression = "sin(((30)*pi/180))"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression, "angle_unit": angle_unit})
        assert response.status_code == 200, response.text
        result = MathResponse.model_validate(response.json())
        assert result.success and result.result_type.value == "scalar", result
        exact = sp.sympify(result.result_text)
        assert exact == sp.Rational(1, 2) and not exact.has(sp.Float), result
        assert result.result_latex == r"\frac{1}{2}", result
        assert result.result_approx == 0.5, result
        again = client.post("/api/v1/evaluate", json={"expression": result.result_text, "angle_unit": angle_unit})
        assert again.status_code == 200, again.text
        restored = MathResponse.model_validate(again.json())
        assert restored.success and sp.sympify(restored.result_text) == sp.Rational(1, 2), restored
