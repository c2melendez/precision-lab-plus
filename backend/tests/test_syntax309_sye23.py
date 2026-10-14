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


def test_sye26_sum_of_fractions_exact_http_and_reentry():
    row = ROWS["SY-E-26"]
    assert row["operacion"] == "valor"
    assert row["entrada"] == r"\frac{1}{3}+\frac{1}{6}"
    assert row["esperado"] == r"\frac{1}{2}"
    expression = "(1/3)+(1/6)"  # Explicit translation; original UI conversion verified separately.
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert data["operation"] == "evaluate" and data["result_type"] == "scalar", data
        assert data["input_text"] == expression and data["request_id"], data
        assert sympy.sympify(data["result_text"]) == sympy.Rational(1, 2), data
        assert data["result_latex"] == r"\frac{1}{2}", data
        assert data["result_approx"] == 0.5, data
        assert data["error_code"] is None and data["error_message"] is None, data
        reentry = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert reentry.status_code == 200, reentry.text
        repeated = reentry.json()
        MathResponse.model_validate(repeated)
        assert repeated["success"] is True, repeated
        assert repeated["request_id"] != data["request_id"], repeated
        assert sympy.sympify(repeated["result_text"]) == sympy.Rational(1, 2), repeated
        assert repeated["result_approx"] == 0.5, repeated


def test_sye27_improper_fraction_exact_http_and_reentry():
    row = ROWS["SY-E-27"]
    assert row["operacion"] == "valor"
    assert row["entrada"] == r"\frac{22}{7}"
    assert row["esperado"] == r"\frac{22}{7}\approx3.142857143"
    expression = "22/7"  # Explicit translation; original UI conversion verified separately.
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert data["operation"] == "evaluate" and data["result_type"] == "scalar", data
        assert data["input_text"] == expression and data["request_id"], data
        assert sympy.sympify(data["result_text"]) == sympy.Rational(22, 7), data
        assert data["result_latex"] == r"\frac{22}{7}", data
        assert data["result_approx"] == pytest.approx(22/7, rel=1e-15), data
        assert data["error_code"] is None and data["error_message"] is None, data
        reentry = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert reentry.status_code == 200, reentry.text
        repeated = reentry.json()
        MathResponse.model_validate(repeated)
        assert repeated["success"] is True, repeated
        assert repeated["request_id"] != data["request_id"], repeated
        assert sympy.sympify(repeated["result_text"]) == sympy.Rational(22, 7), repeated
        assert repeated["result_approx"] == pytest.approx(22/7, rel=1e-15), repeated

def test_sye28_original_zero_denominator_domain_error_and_recovery():
    row = ROWS["SY-E-28"]
    assert row["operacion"] == "error"
    assert row["entrada"] == r"\frac{1}{0}"
    assert "división entre cero" in row["esperado"]
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "1/0"})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is False, data
        assert data["error_code"] == "DOMAIN_ERROR", data
        assert any(term in data["error_message"].lower() for term in ("cero", "zero", "divisi")), data
        assert data["result_text"] is None and data["result_latex"] is None, data
        assert data["result_approx"] is None, data
        recovered_response = client.post("/api/v1/evaluate", json={"expression": "2+3"})
        assert recovered_response.status_code == 200, recovered_response.text
        recovered = recovered_response.json()
        MathResponse.model_validate(recovered)
        assert recovered["success"] is True and recovered["result_approx"] == 5, recovered
        assert recovered["request_id"] != data["request_id"], (data, recovered)


def test_sye29_zero_over_zero_indeterminate_error_and_recovery():
    row = ROWS["SY-E-29"]
    assert row["operacion"] == "error"
    assert row["entrada"] == r"\frac{0}{0}"
    assert "indeterminado" in row["esperado"]
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression":"0/0"})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is False, data
        assert data["error_code"] == "DOMAIN_ERROR", data
        assert any(s in (data["error_message"] or "").lower() for s in ("indeterm", "0/0")), data
        assert data["result_text"] is None and data["result_latex"] is None, data
        assert data["result_approx"] is None, data
        response2 = client.post("/api/v1/evaluate", json={"expression":"2+3"})
        assert response2.status_code == 200, response2.text
        recovered = response2.json()
        MathResponse.model_validate(recovered)
        assert recovered["success"] is True and recovered["result_approx"] == 5, recovered
        assert recovered["request_id"] != data["request_id"], (data,recovered)


def test_sye31_fraction_adjacency_declared_as_product_and_reentry():
    row = ROWS["SY-E-31"]
    assert row["operacion"] == "convencion"
    assert row["entrada"] == r"2\frac{1}{3}"
    assert "Número mixto o producto: declarar" in row["nota"]
    # The frontend converts adjacency to multiplication; not mixed-number addition.
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "2*(1/3)"})
        assert response.status_code == 200, response.text
        result = response.json()
        MathResponse.model_validate(result)
        assert result["success"] is True, result
        assert sympy.sympify(result["result_text"]) == sympy.Rational(2, 3), result
        assert result["result_approx"] == pytest.approx(2/3), result
        again = client.post("/api/v1/evaluate", json={"expression": result["result_text"]})
        assert again.status_code == 200, again.text
        repeated = again.json()
        MathResponse.model_validate(repeated)
        assert repeated["success"] is True, repeated
        assert sympy.sympify(repeated["result_text"]) == sympy.Rational(2, 3), repeated


def test_syn01_leading_decimal_http_and_reentry():
    row = ROWS["SY-N-01"]
    assert row["operacion"] == "valor"
    assert row["entrada"] == ".5"
    assert row["esperado"] == "0.5"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": ".5"})
        assert response.status_code == 200, response.text
        value = response.json()
        MathResponse.model_validate(value)
        assert value["success"] is True, value
        assert sympy.sympify(value["result_text"]) == sympy.Rational(1,2), value
        assert value["result_approx"] == 0.5, value
        again = client.post("/api/v1/evaluate", json={"expression": value["result_text"]})
        assert again.status_code == 200, again.text
        result = again.json()
        MathResponse.model_validate(result)
        assert result["success"] is True, result
        assert result["result_approx"] == 0.5, result


def test_syn02_trailing_decimal_http_and_reentry():
    row = ROWS["SY-N-02"]
    assert row["operacion"] == "valor"
    assert row["entrada"] == "5."
    assert row["esperado"] == "5"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code == 200, response.text
        value = response.json()
        MathResponse.model_validate(value)
        assert value["success"] is True, value
        assert sympy.sympify(value["result_text"]) == sympy.Integer(5), value
        assert value["result_approx"] == 5, value
        assert value["error_code"] is None, value
        again = client.post("/api/v1/evaluate", json={"expression": value["result_text"]})
        assert again.status_code == 200, again.text
        repeated = again.json()
        MathResponse.model_validate(repeated)
        assert repeated["success"] is True, repeated
        assert sympy.sympify(repeated["result_text"]) == sympy.Integer(5), repeated


def test_syn03_leading_zero_integer_http_and_reentry():
    row = ROWS["SY-N-03"]
    assert row["operacion"] == "valor"
    assert row["entrada"] == "00012"
    assert row["esperado"] == "12"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code == 200, response.text
        result = response.json()
        MathResponse.model_validate(result)
        assert result["success"] is True, result
        assert sympy.sympify(result["result_text"]) == sympy.Integer(12), result
        assert result["result_approx"] == 12, result
        again = client.post("/api/v1/evaluate", json={"expression": result["result_text"]})
        assert again.status_code == 200, again.text
        repeated = again.json()
        MathResponse.model_validate(repeated)
        assert repeated["success"] is True, repeated
        assert sympy.sympify(repeated["result_text"]) == sympy.Integer(12), repeated


def test_syn04_scientific_multiplication_http_and_reentry():
    row = ROWS["SY-N-04"]
    assert row["operacion"] == "valor"
    assert row["entrada"] == r"1.2\times10^{3}"
    assert row["esperado"] == "1200"
    # The UI converts LaTeX multiplication/exponents to this backend expression.
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "1.2*10^3"})
        assert response.status_code == 200, response.text
        result = response.json()
        MathResponse.model_validate(result)
        assert result["success"] is True, result
        assert sympy.sympify(result["result_text"]) == sympy.Integer(1200), result
        assert result["result_approx"] == 1200, result
        again = client.post("/api/v1/evaluate", json={"expression": result["result_text"]})
        assert again.status_code == 200, again.text
        repeated = again.json()
        MathResponse.model_validate(repeated)
        assert repeated["success"] is True, repeated
        assert sympy.sympify(repeated["result_text"]) == sympy.Integer(1200), repeated


def test_syn05_explicit_calculator_e_http_and_reentry():
    row = ROWS["SY-N-05"]
    assert row["operacion"] == "convencion"
    assert row["entrada"] == r"1\mathrm{e}3"
    assert "1000" in row["esperado"]
    # UI translation is independently covered by the frontend test.
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "1000"})
        assert response.status_code == 200, response.text
        result = response.json()
        MathResponse.model_validate(result)
        assert result["success"] is True, result
        assert sympy.sympify(result["result_text"]) == sympy.Integer(1000), result
        assert result["result_approx"] == 1000, result
        again = client.post("/api/v1/evaluate", json={"expression": result["result_text"]})
        assert again.status_code == 200, again.text
        repeated = again.json()
        MathResponse.model_validate(repeated)
        assert repeated["success"] is True, repeated
        assert sympy.sympify(repeated["result_text"]) == sympy.Integer(1000), repeated


def test_syn06_exact_decimal_addition_http_and_reentry():
    row = ROWS["SY-N-06"]
    assert row["operacion"] == "valor"
    assert row["entrada"] == "0.1+0.2"
    assert row["esperado"] == "0.3"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code == 200, response.text
        result = response.json()
        MathResponse.model_validate(result)
        assert result["success"] is True, result
        assert sympy.sympify(result["result_text"]) == sympy.Rational(3, 10), result
        assert result["result_approx"] == 0.3, result
        assert "0.30000000000000004" not in str(result), result
        again = client.post("/api/v1/evaluate", json={"expression": result["result_text"]})
        assert again.status_code == 200, again.text
        repeated = again.json()
        MathResponse.model_validate(repeated)
        assert repeated["success"] is True, repeated
        assert sympy.sympify(repeated["result_text"]) == sympy.Rational(3, 10), repeated


def test_syn07_decimal_multiplication_http_and_reentry():
    row = ROWS["SY-N-07"]
    assert row["operacion"] == "valor"
    assert row["entrada"] == r"0.1\times3"
    assert row["esperado"] == "0.3"
    # Explicit frontend-to-backend translation of the original LaTeX multiplication.
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "0.1*3"})
        assert response.status_code == 200, response.text
        result = response.json()
        MathResponse.model_validate(result)
        assert result["success"] is True, result
        assert sympy.sympify(result["result_text"]) == sympy.Rational(3, 10), result
        assert result["result_approx"] == 0.3, result
        assert "0.30000000000000004" not in str(result), result
        again = client.post("/api/v1/evaluate", json={"expression": result["result_text"]})
        assert again.status_code == 200, again.text
        repeated = again.json()
        MathResponse.model_validate(repeated)
        assert repeated["success"] is True, repeated
        assert sympy.sympify(repeated["result_text"]) == sympy.Rational(3, 10), repeated


def test_syn08_decimal_subtraction_http_and_reentry():
    row = ROWS["SY-N-08"]
    assert row["operacion"] == "valor"
    assert row["entrada"] == "1-0.9"
    assert row["esperado"] == "0.1"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code == 200, response.text
        result = response.json()
        MathResponse.model_validate(result)
        assert result["success"] is True, result
        assert sympy.sympify(result["result_text"]) == sympy.Rational(1, 10), result
        assert result["result_approx"] == 0.1, result
        assert "0.09999999999999998" not in str(result), result
        again = client.post("/api/v1/evaluate", json={"expression": result["result_text"]})
        assert again.status_code == 200, again.text
        repeated = again.json()
        MathResponse.model_validate(repeated)
        assert repeated["success"] is True, repeated
        assert sympy.sympify(repeated["result_text"]) == sympy.Rational(1, 10), repeated


def test_syn09_decimal_product_http_exact_and_reentry():
    row = ROWS["SY-N-09"]
    assert row["operacion"] == "valor"
    assert row["entrada"] == r"4.35\times100"
    assert row["esperado"] == "435"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "4.35*100"})
        assert response.status_code == 200, response.text
        result = response.json()
        MathResponse.model_validate(result)
        assert result["success"] is True, result
        assert sympy.sympify(result["result_text"]) == sympy.Integer(435), result
        assert result["result_approx"] == 435, result
        assert "434.99999999999994" not in str(result), result
        again = client.post("/api/v1/evaluate", json={"expression": result["result_text"]})
        assert again.status_code == 200, again.text
        repeated = again.json()
        MathResponse.model_validate(repeated)
        assert repeated["success"] is True, repeated
        assert sympy.sympify(repeated["result_text"]) == sympy.Integer(435), repeated


def test_syn10_decimal_product_exact_http_and_result_reentry():
    row = ROWS["SY-N-10"]
    assert row["operacion"] == "valor"
    assert row["entrada"] == r"1.005\times1000"
    assert row["esperado"] == "1005"
    # Explicit backend translation; original LaTeX converter tested independently.
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "1.005*1000"})
        assert response.status_code == 200, response.text
        result = response.json()
        MathResponse.model_validate(result)
        assert result["success"] is True, result
        assert result["operation"] == "evaluate" and result["result_type"] == "scalar", result
        assert result["input_text"] == "1.005*1000" and result["request_id"], result
        assert result["result_text"] == "1005" and result["result_latex"] == "1005", result
        assert result["result_approx"] == 1005, result
        assert result["error_code"] is None and result["error_message"] is None, result
        again = client.post("/api/v1/evaluate", json={"expression": result["result_text"]})
        assert again.status_code == 200, again.text
        repeated = again.json()
        MathResponse.model_validate(repeated)
        assert repeated["success"] is True, repeated
        assert repeated["request_id"] != result["request_id"], repeated
        assert repeated["result_text"] == "1005" and repeated["result_latex"] == "1005", repeated
        assert repeated["result_approx"] == 1005, repeated


def test_syn11_exact_third_times_three_http_and_reentry():
    row = ROWS["SY-N-11"]
    assert row["operacion"] == "valor"
    assert row["entrada"] == r"\frac{1}{3}\times3"
    assert row["esperado"] == "1"
    expression = "(1/3)*3"  # Original LaTeX conversion tested separately.
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
        assert response.status_code == 200, response.text
        result = response.json()
        MathResponse.model_validate(result)
        assert result["success"] is True, result
        assert result["operation"] == "evaluate" and result["result_type"] == "scalar", result
        assert result["input_text"] == expression and result["request_id"], result
        assert result["result_text"] == "1" and result["result_latex"] == "1", result
        assert result["result_approx"] == 1, result
        assert result["error_code"] is None and result["error_message"] is None, result
        again = client.post("/api/v1/evaluate", json={"expression": result["result_text"]})
        assert again.status_code == 200, again.text
        repeated = again.json()
        MathResponse.model_validate(repeated)
        assert repeated["success"] is True, repeated
        assert repeated["request_id"] != result["request_id"], repeated
        assert repeated["result_text"] == "1" and repeated["result_latex"] == "1", repeated
        assert repeated["result_approx"] == 1, repeated


def test_syn12_decimal_plus_abbreviated_fraction_http_and_reentry():
    row = ROWS["SY-N-12"]
    assert row["operacion"] == "valor"
    assert row["entrada"] == r"1.5+\frac12"
    assert row["esperado"] == "2"
    expression = "1.5+1/2"  # Original LaTeX conversion tested separately.
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
        assert response.status_code == 200, response.text
        result = response.json()
        MathResponse.model_validate(result)
        assert result["success"] is True, result
        assert result["operation"] == "evaluate" and result["result_type"] == "scalar", result
        assert result["input_text"] == expression and result["request_id"], result
        assert result["result_text"] == "2" and result["result_latex"] == "2", result
        assert result["result_approx"] == 2, result
        assert result["error_code"] is None and result["error_message"] is None, result
        again = client.post("/api/v1/evaluate", json={"expression": result["result_text"]})
        assert again.status_code == 200, again.text
        repeated = again.json()
        MathResponse.model_validate(repeated)
        assert repeated["success"] is True, repeated
        assert repeated["request_id"] != result["request_id"], repeated
        assert repeated["result_text"] == "2" and repeated["result_latex"] == "2", repeated
        assert repeated["result_approx"] == 2, repeated


def test_syn13_squared_radical_http_exact_and_reentry():
    row = ROWS["SY-N-13"]
    assert row["operacion"] == "valor"
    assert row["entrada"] == r"\sqrt{2}^{2}"
    assert row["esperado"] == "2"
    expression = "sqrt(2)^2"  # LaTeX conversion tested separately in frontend.
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
        assert response.status_code == 200, response.text
        result = response.json()
        MathResponse.model_validate(result)
        assert result["success"] is True, result
        assert result["operation"] == "evaluate" and result["result_type"] == "scalar", result
        assert result["input_text"] == expression and result["request_id"], result
        assert result["result_text"] == "2" and result["result_latex"] == "2", result
        assert result["result_approx"] == 2, result
        assert "2.0000000000000004" not in str(result), result
        assert result["error_code"] is None and result["error_message"] is None, result
        again = client.post("/api/v1/evaluate", json={"expression": result["result_text"]})
        assert again.status_code == 200, again.text
        repeated = again.json()
        MathResponse.model_validate(repeated)
        assert repeated["success"] is True, repeated
        assert repeated["request_id"] != result["request_id"], repeated
        assert repeated["result_text"] == "2" and repeated["result_latex"] == "2", repeated
        assert repeated["result_approx"] == 2, repeated


def test_syn14_squared_radical_minus_two_http_exact_zero_and_reentry():
    row = ROWS["SY-N-14"]
    assert row["operacion"] == "valor"
    assert row["entrada"] == r"\left(\sqrt{2}\right)^{2}-2"
    assert row["esperado"] == "0"
    expression = "(sqrt(2))^2-2"  # Frontend original source conversion tested independently.
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
        assert response.status_code == 200, response.text
        result = response.json()
        MathResponse.model_validate(result)
        assert result["success"] is True, result
        assert result["operation"] == "evaluate" and result["result_type"] == "scalar", result
        assert result["input_text"] == expression and result["request_id"], result
        assert result["result_text"] == "0" and result["result_latex"] == "0", result
        assert result["result_approx"] == 0, result
        assert result["error_code"] is None and result["error_message"] is None, result
        again = client.post("/api/v1/evaluate", json={"expression": result["result_text"]})
        assert again.status_code == 200, again.text
        repeated = again.json()
        MathResponse.model_validate(repeated)
        assert repeated["success"] is True, repeated
        assert repeated["request_id"] != result["request_id"], repeated
        assert repeated["result_text"] == "0" and repeated["result_latex"] == "0", repeated
        assert repeated["result_approx"] == 0, repeated


def test_syn15_large_integer_http_exact_and_reentry():
    row = ROWS["SY-N-15"]
    assert row["operacion"] == "valor"
    assert row["entrada"] == "10^{20}+1"
    assert row["esperado"] == "100000000000000000001"
    expression = "10^20+1"  # Original LaTeX conversion independently tested.
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
        assert response.status_code == 200, response.text
        result = response.json()
        MathResponse.model_validate(result)
        assert result["success"] is True, result
        assert result["operation"] == "evaluate" and result["result_type"] == "scalar", result
        assert result["input_text"] == expression and result["request_id"], result
        assert result["result_text"] == row["esperado"], result
        assert result["result_latex"] == row["esperado"], result
        assert result["error_code"] is None and result["error_message"] is None, result
        again = client.post("/api/v1/evaluate", json={"expression": result["result_text"]})
        assert again.status_code == 200, again.text
        repeated = again.json()
        MathResponse.model_validate(repeated)
        assert repeated["success"] is True, repeated
        assert repeated["request_id"] != result["request_id"], repeated
        assert repeated["result_text"] == row["esperado"], repeated
        assert repeated["result_latex"] == row["esperado"], repeated


def test_syn16_power_of_two_exact_http_and_reentry():
    row = ROWS["SY-N-16"]
    expected = "1267650600228229401496703205376"
    assert row["operacion"] == "valor"
    assert row["entrada"] == r"2^{100}"
    assert row["esperado"] == expected
    with TestClient(app) as client:
        reply = client.post("/api/v1/evaluate", json={"expression": "2^100"})
        assert reply.status_code == 200, reply.text
        result = reply.json()
        MathResponse.model_validate(result)
        assert result["success"] is True, result
        assert result["result_text"] == expected and result["result_latex"] == expected, result
        assert result["request_id"] and result["error_code"] is None, result
        again = client.post("/api/v1/evaluate", json={"expression": result["result_text"]})
        assert again.status_code == 200, again.text
        repeated = again.json()
        MathResponse.model_validate(repeated)
        assert repeated["success"] is True, repeated
        assert repeated["request_id"] != result["request_id"], repeated
        assert repeated["result_text"] == expected and repeated["result_latex"] == expected, repeated
