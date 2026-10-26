"""SY-R-14: absolute-value semantics, sign controls and exact HTTP reentry."""
import os
import pytest
import sympy as sp
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse

@pytest.mark.parametrize("payload, expected", [
    ({"expression": r"\left\lvert x\right\rvert\ \text{con}\ x=-4"}, sp.Integer(4)),
    ({"expression": "(abs(x)) con x=(-4)"}, sp.Integer(4)),
    ({"expression": r"\left\lvert x\right\rvert", "substitutions": {"x": "-4"}}, sp.Integer(4)),
    ({"expression": r"\left\lvert x\right\rvert\ \text{con}\ x=4"}, sp.Integer(4)),
    ({"expression": r"\left\lvert y\right\rvert\ \text{con}\ y=-7"}, sp.Integer(7)),
    ({"expression": r"\left\lvert x\right\rvert\ \text{con}\ x=0"}, sp.Integer(0)),
    ({"expression": r"\left\lvert x\right\rvert\ \text{con}\ x=-\frac{3}{2}"}, sp.Rational(3, 2)),
    ({"expression": r"\left\lvert x\right\rvert+x\ \text{con}\ x=-4"}, sp.Integer(0)),
    ({"expression": r"\left\lvert x\right\rvert+x\ \text{con}\ x=4"}, sp.Integer(8)),
])
def test_syr14_absolute_value_sign_and_reentry(payload, expected):
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


@pytest.mark.parametrize("source", [
    r"\left\lvert x\rvert\ \text{con}\ x=-4",
    r"\lvert x\right\rvert\ \text{con}\ x=-4",
])
def test_syr14_rejects_unpaired_sizing_delimiters(source):
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": source})
        assert response.status_code == 200, response.text
        result = MathResponse.model_validate(response.json())
        assert not result.success and result.error_code.value == "PARSE_ERROR", result
        assert result.error_message, result
