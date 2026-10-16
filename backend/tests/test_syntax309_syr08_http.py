"""SY-R-08: exact complex components and public result_text reentry."""
import os
import pytest
import sympy as sp
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse

@pytest.mark.parametrize("witness, real, imag", [
    ("1+2i", 1, 2),
    ("1+2*i", 1, 2),
    ("3-4i", 3, -4),
    ("-2+3i", -2, 3),
    ("(1+2i)^2", -3, 4),
])
def test_syr08_exact_complex_components_and_reentry(witness, real, imag):
    def check(result):
        assert result.success and result.result_type.value == "scalar", result
        assert result.result_latex, result
        actual = sp.sympify(result.result_text, locals={"i": sp.I, "I": sp.I})
        assert not actual.free_symbols and not actual.has(sp.Float), result
        assert sp.simplify(sp.re(actual) - real) == 0, result
        assert sp.simplify(sp.im(actual) - imag) == 0, result
        assert sp.simplify(actual - (real + imag * sp.I)) == 0, result
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": witness, "angle_unit": "rad"})
        assert response.status_code == 200, response.text
        result = MathResponse.model_validate(response.json())
        check(result)
        again = client.post("/api/v1/evaluate", json={"expression": result.result_text, "angle_unit": "rad"})
        assert again.status_code == 200, again.text
        check(MathResponse.model_validate(again.json()))
