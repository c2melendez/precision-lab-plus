"""SY-E-23 numeric nested fraction: explicit HTTP translation, exact and round-trip."""
import json
import os
from pathlib import Path

os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")

import pytest
import sympy
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.responses import MathResponse

DATA = Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl"
ROWS = {row["id"]: row for row in
        (json.loads(line) for line in DATA.read_text(encoding="utf-8").splitlines() if line.strip())}

def test_sye23_nested_numeric_fraction_exact_http_and_reentry():
    row = ROWS["SY-E-23"]
    assert row["operacion"] == "valor"
    assert row["entrada"] == r"\frac{\frac{1}{2}}{\frac{3}{4}}"
    assert row["esperado"] == r"\frac{2}{3}"
    expression = "(1/2)/(3/4)"  # Explicit translation: not evidence of native MathLive.
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert data["operation"] == "evaluate" and data["result_type"] == "scalar", data
        assert data["input_text"] == expression and data["request_id"], data
        assert data["error_code"] is None and data["error_message"] is None, data
        assert sympy.sympify(data["result_text"]) == sympy.Rational(2, 3), data
        assert data["result_latex"] == r"\frac{2}{3}", data
        assert data["result_approx"] == pytest.approx(2/3, rel=1e-15), data
        assert isinstance(data["steps"], list) and isinstance(data["warnings"], list), data
        assert isinstance(data["has_detailed_steps"], bool), data
        assert isinstance(data["domain_conditions"], list), data

        reentry = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert reentry.status_code == 200, reentry.text
        result2 = reentry.json()
        MathResponse.model_validate(result2)
        assert result2["success"] is True, result2
        assert result2["request_id"] != data["request_id"], result2
        assert sympy.sympify(result2["result_text"]) == sympy.Rational(2, 3), result2
        assert result2["result_approx"] == pytest.approx(2/3, rel=1e-15), result2


def test_sye24_display_fraction_exact_http_and_reentry():
    row = ROWS["SY-E-24"]
    assert row["operacion"] == "valor"
    assert row["entrada"] == r"\dfrac{3}{4}"
    assert row["esperado"] == r"\frac{3}{4}"
    expression = "(3)/(4)"  # Explicit translation; original UI conversion verified separately.
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert data["operation"] == "evaluate" and data["result_type"] == "scalar", data
        assert data["input_text"] == expression and data["request_id"], data
        assert sympy.sympify(data["result_text"]) == sympy.Rational(3, 4), data
        assert data["result_latex"] == r"\frac{3}{4}", data
        assert data["result_approx"] == 0.75, data
        assert data["error_code"] is None and data["error_message"] is None, data
        reentry = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert reentry.status_code == 200, reentry.text
        repeated = reentry.json()
        MathResponse.model_validate(repeated)
        assert repeated["success"] is True, repeated
        assert repeated["request_id"] != data["request_id"], repeated
        assert sympy.sympify(repeated["result_text"]) == sympy.Rational(3, 4), repeated
        assert repeated["result_approx"] == 0.75, repeated


def test_sye25_text_fraction_exact_http_and_reentry():
    row = ROWS["SY-E-25"]
    assert row["operacion"] == "valor"
    assert row["entrada"] == r"\tfrac{3}{4}"
    assert row["esperado"] == r"\frac{3}{4}"
    expression = "(3)/(4)"  # Explicit translation; original UI conversion verified separately.
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert data["operation"] == "evaluate" and data["result_type"] == "scalar", data
        assert data["input_text"] == expression and data["request_id"], data
        assert sympy.sympify(data["result_text"]) == sympy.Rational(3, 4), data
        assert data["result_latex"] == r"\frac{3}{4}", data
        assert data["result_approx"] == 0.75, data
        assert data["error_code"] is None and data["error_message"] is None, data
        reentry = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert reentry.status_code == 200, reentry.text
        repeated = reentry.json()
        MathResponse.model_validate(repeated)
        assert repeated["success"] is True, repeated
        assert repeated["request_id"] != data["request_id"], repeated
        assert sympy.sympify(repeated["result_text"]) == sympy.Rational(3, 4), repeated
        assert repeated["result_approx"] == 0.75, repeated
