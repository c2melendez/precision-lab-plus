"""SY-R-13: exact cube-root substitution, converter witness and HTTP reentry."""
import os
import pytest
import sympy as sp
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse

@pytest.mark.parametrize("payload, expected", [
    ({"expression": r"\sqrt[3]{x}\ \text{con}\ x=27"}, sp.Integer(3)),
    ({"expression": "((x)**(1/(3))) con x=(27)"}, sp.Integer(3)),
    ({"expression": r"\sqrt[3]{x}", "substitutions": {"x": "27"}}, sp.Integer(3)),
    ({"expression": r"\sqrt[3]{x}\ \text{con}\ x=8"}, sp.Integer(2)),
    ({"expression": r"\sqrt[3]{y}\ \text{con}\ y=64"}, sp.Integer(4)),
    ({"expression": r"\sqrt[3]{x}\ \text{con}\ x=\frac{1}{8}"}, sp.Rational(1, 2)),
    ({"expression": r"\sqrt[3]{x}\ \text{con}\ x=0"}, sp.Integer(0)),
])
def test_syr13_exact_value_and_result_text_reentry(payload, expected):
    def check(result):
        assert result.success and result.result_type.value == "scalar" and result.result_latex, result
        actual = sp.sympify(result.result_text)
        assert not actual.free_symbols and not actual.has(sp.Float), result
        assert sp.simplify(actual - expected) == 0, result
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json=payload)
        assert response.status_code == 200, response.text
        first = MathResponse.model_validate(response.json())
        check(first)
        response = client.post("/api/v1/evaluate", json={"expression": first.result_text})
        assert response.status_code == 200, response.text
        check(MathResponse.model_validate(response.json()))
