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


def test_syn17_unsafe_js_integer_stays_exact_http_and_reentry():
    row = ROWS["SY-N-17"]
    expected = "9007199254740993"
    assert row["operacion"] == "valor"
    assert row["entrada"] == expected
    assert row["esperado"] == expected
    with TestClient(app) as client:
        reply = client.post("/api/v1/evaluate", json={"expression": expected})
        assert reply.status_code == 200, reply.text
        result = reply.json()
        MathResponse.model_validate(result)
        assert result["success"] is True, result
        assert result["result_text"] == expected and result["result_latex"] == expected, result
        assert result["error_code"] is None, result
        again = client.post("/api/v1/evaluate", json={"expression": result["result_text"]})
        assert again.status_code == 200, again.text
        repeated = again.json()
        MathResponse.model_validate(repeated)
        assert repeated["success"] is True, repeated
        assert repeated["request_id"] != result["request_id"], repeated
        assert repeated["result_text"] == expected and repeated["result_latex"] == expected, repeated


def test_syn18_percent_exact_http_and_reentry():
    row = ROWS["SY-N-18"]
    assert row["entrada"] == r"12\%"
    assert row["esperado"] == "0.12"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "12/100"})
        assert response.status_code == 200, response.text
        result = response.json()
        MathResponse.model_validate(result)
        assert result["success"] is True, result
        assert sympy.sympify(result["result_text"]) == sympy.Rational(3, 25), result
        assert result["result_approx"] == 0.12, result
        again = client.post("/api/v1/evaluate", json={"expression": result["result_text"]})
        assert again.status_code == 200, again.text
        repeated = again.json()
        MathResponse.model_validate(repeated)
        assert repeated["success"] is True, repeated
        assert sympy.sympify(repeated["result_text"]) == sympy.Rational(3, 25), repeated


def test_syn19_percent_multiplication_http_and_reentry():
    row = ROWS["SY-N-19"]
    assert row["operacion"] == "valor"
    assert row["entrada"] == r"50\%\times200"
    assert row["esperado"] == "100"
    expression = "(50/100)*200"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
        assert response.status_code == 200, response.text
        result = response.json()
        MathResponse.model_validate(result)
        assert result["success"] is True, result
        assert result["result_text"] == "100" and result["result_latex"] == "100", result
        assert result["result_approx"] == 100, result
        assert result["error_code"] is None and result["error_message"] is None, result
        again = client.post("/api/v1/evaluate", json={"expression": result["result_text"]})
        assert again.status_code == 200, again.text
        repeated = again.json()
        MathResponse.model_validate(repeated)
        assert repeated["success"] is True, repeated
        assert repeated["result_text"] == "100" and repeated["result_latex"] == "100", repeated


def test_syn20_factorial_five_http_and_reentry():
    row = ROWS["SY-N-20"]
    assert row["operacion"] == "valor"
    assert row["entrada"] == "5!"
    assert row["esperado"] == "120"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "5!"})
        assert response.status_code == 200, response.text
        result = response.json()
        MathResponse.model_validate(result)
        assert result["success"] is True, result
        assert result["result_text"] == "120" and result["result_latex"] == "120", result
        assert result["result_approx"] == 120, result
        assert result["error_code"] is None and result["error_message"] is None, result
        again = client.post("/api/v1/evaluate", json={"expression": result["result_text"]})
        assert again.status_code == 200, again.text
        repeated = again.json()
        MathResponse.model_validate(repeated)
        assert repeated["success"] is True, repeated
        assert repeated["result_text"] == "120" and repeated["result_latex"] == "120", repeated



def test_syn21_zero_factorial_http_and_reentry():
    row = ROWS["SY-N-21"]
    assert row["operacion"] == "valor"
    assert row["entrada"] == "0!"
    assert row["esperado"] == "1"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "0!"})
        assert response.status_code == 200, response.text
        result = response.json()
        MathResponse.model_validate(result)
        assert result["success"] is True, result
        assert result["operation"] == "evaluate" and result["result_type"] == "scalar", result
        assert result["input_text"] == "0!" and result["request_id"], result
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



def test_syn22_negative_factorial_http_error_and_recovery():
    row = ROWS["SY-N-22"]
    assert row["operacion"] == "error"
    assert row["entrada"] == "(-1)!"
    assert "factorial no definido" in row["esperado"]
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "(-1)!"})
        assert response.status_code in (200, 400, 422), response.text
        result = response.json()
        MathResponse.model_validate(result)
        assert result["success"] is False, result
        assert result["request_id"], result
        assert result["error_code"] in ("DOMAIN_ERROR", "VALIDATION_ERROR"), result
        assert result["error_message"] and any(
            word in result["error_message"].lower()
            for word in ("factorial", "negative", "negativo", "domain", "dominio", "definido")
        ), result
        assert result.get("result_text") in (None, ""), result
        again = client.post("/api/v1/evaluate", json={"expression": "2+3"})
        assert again.status_code == 200, again.text
        recovered = again.json()
        MathResponse.model_validate(recovered)
        assert recovered["success"] is True, recovered
        assert recovered["result_text"] == "5" and recovered["result_latex"] == "5", recovered
        assert recovered["request_id"] != result["request_id"], recovered



def test_syn23_non_integer_factorial_gamma_or_clear_error_and_recovery():
    row = ROWS["SY-N-23"]
    assert row["operacion"] == "convencion"
    assert row["entrada"] == "2.5!"
    assert "Gamma o aviso" in row["nota"]
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "2.5!"})
        assert response.status_code in (200, 400, 422), response.text
        result = response.json()
        MathResponse.model_validate(result)
        assert result["request_id"], result
        if result["success"]:
            assert response.status_code == 200, result
            assert result["error_code"] is None, result
            assert result["result_approx"] == pytest.approx(3.3233509704478426, rel=1e-8), result
        else:
            assert result["error_code"] in ("DOMAIN_ERROR", "VALIDATION_ERROR", "UNSUPPORTED_OPERATION"), result
            assert result["error_message"] and any(word in result["error_message"].lower()
                for word in ("factorial", "gamma", "integer", "entero", "domain", "dominio")), result
            assert result.get("result_text") in (None, ""), result
        again = client.post("/api/v1/evaluate", json={"expression": "2+3"})
        assert again.status_code == 200, again.text
        recovered = again.json()
        MathResponse.model_validate(recovered)
        assert recovered["success"] is True, recovered
        assert recovered["result_text"] == "5", recovered
        assert recovered["request_id"] != result["request_id"], recovered



def test_syn24_hundred_factorial_exact_or_valid_scientific_and_recovery():
    import math
    row = ROWS["SY-N-24"]
    assert row["operacion"] == "valor"
    assert row["entrada"] == "100!"
    assert "158 dígitos" in row["nota"]
    exact = str(math.factorial(100))
    assert len(exact) == 158
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "100!"})
        assert response.status_code == 200, response.text
        result = response.json()
        MathResponse.model_validate(result)
        assert result["success"] is True, result
        assert result["request_id"] and result["error_code"] is None, result
        numeric = result["result_approx"]
        assert result["result_text"] == exact or (
            numeric is not None and math.isfinite(numeric)
            and numeric == pytest.approx(9.332621544394415e157, rel=1e-8)
        ), result
        assert "Infinity" not in str(result) and "NaN" not in str(result), result
        again = client.post("/api/v1/evaluate", json={"expression": "2+3"})
        assert again.status_code == 200, again.text
        recovered = again.json()
        MathResponse.model_validate(recovered)
        assert recovered["success"] is True and recovered["result_text"] == "5", recovered



def test_syn25_factorial_170_finite_exact_or_approx_and_recovery():
    import math
    row = ROWS["SY-N-25"]
    assert row["operacion"] == "valor"
    assert row["entrada"] == "170!"
    exact = str(math.factorial(170))
    assert len(exact) == 307
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "170!"})
        assert response.status_code == 200, response.text
        result = response.json()
        MathResponse.model_validate(result)
        assert result["success"] is True, result
        assert result["request_id"] and result["error_code"] is None, result
        numeric = result["result_approx"]
        assert result["result_text"] == exact or (
            numeric is not None and math.isfinite(numeric)
            and numeric == pytest.approx(7.257415615307999e306, rel=1e-8)
        ), result
        assert "Infinity" not in str(result) and "NaN" not in str(result), result
        again = client.post("/api/v1/evaluate", json={"expression": "2+3"})
        assert again.status_code == 200, again.text
        recovered = again.json()
        MathResponse.model_validate(recovered)
        assert recovered["success"] is True and recovered["result_text"] == "5", recovered



def test_syn26_factorial_171_exact_or_explicit_overflow_and_recovery():
    import math
    row = ROWS["SY-N-26"]
    assert row["entrada"] == "171!"
    exact = str(math.factorial(171))
    assert len(exact) == 310
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "171!"})
        assert response.status_code in (200, 400, 422), response.text
        result = response.json()
        MathResponse.model_validate(result)
        assert result["request_id"], result
        assert "Infinity" not in str(result) and "NaN" not in str(result), result
        # Plus now supports this bounded exact result beyond float range.
        assert result["success"] is True, result
        assert result["result_text"] == exact, result
        assert result["result_latex"] == exact, result
        assert result["result_approx"] is None, result
        assert result["error_code"] is None and result["error_message"] is None, result
        again = client.post("/api/v1/evaluate", json={"expression": "2+3"})
        assert again.status_code == 200, again.text
        recovered = again.json()
        MathResponse.model_validate(recovered)
        assert recovered["success"] is True and recovered["result_text"] == "5", recovered


def test_syn27_pi_exact_identity_approximation_and_http_reentry():
    import math
    row = ROWS["SY-N-27"]
    assert row["entrada"] == r"\pi"
    assert row["esperado"] == "3.141592654"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "pi"})
        assert response.status_code == 200, response.text
        result = response.json()
        MathResponse.model_validate(result)
        assert result["success"] is True, result
        assert result["result_text"] == "pi" and result["result_latex"] == r"\pi", result
        assert math.isfinite(result["result_approx"]), result
        assert abs(result["result_approx"] - 3.141592653589793) < 5e-10, result
        assert format(result["result_approx"], ".9f") == "3.141592654", result
        assert result["error_code"] is None and result["error_message"] is None, result
        again = client.post("/api/v1/evaluate", json={"expression": result["result_text"]})
        assert again.status_code == 200, again.text
        repeated = again.json()
        MathResponse.model_validate(repeated)
        assert repeated["success"] is True, repeated
        assert repeated["request_id"] != result["request_id"], repeated
        assert repeated["result_text"] == "pi", repeated
        assert format(repeated["result_approx"], ".9f") == "3.141592654", repeated


def test_syn28_euler_identity_decimal_and_http_reentry():
    import math
    row = ROWS["SY-N-28"]
    assert row["entrada"] == "e"
    assert row["esperado"] == "2.718281828"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code == 200, response.text
        result = response.json()
        MathResponse.model_validate(result)
        assert result["success"] is True, result
        assert sympy.sympify(result["result_text"], locals={"e": sympy.E}) == sympy.E, result
        assert result["result_latex"] == "e", result
        assert math.isfinite(result["result_approx"]), result
        assert abs(result["result_approx"] - 2.718281828459045) < 5e-10, result
        assert format(result["result_approx"], ".9f") == "2.718281828", result
        assert result["error_code"] is None and result["error_message"] is None, result
        # Use the actual displayed LaTeX e, whose conversion is tested separately.
        again = client.post("/api/v1/evaluate", json={"expression": result["result_latex"]})
        assert again.status_code == 200, again.text
        repeated = again.json()
        MathResponse.model_validate(repeated)
        assert repeated["success"] is True, repeated
        assert repeated["request_id"] != result["request_id"], repeated
        assert sympy.sympify(repeated["result_text"], locals={"e": sympy.E}) == sympy.E, repeated
        assert format(repeated["result_approx"], ".9f") == "2.718281828", repeated


def test_syn29_decimal_comma_explicit_http_convention_and_recovery():
    row = ROWS["SY-N-29"]
    assert row["entrada"] == "1,5+2"
    assert row["operacion"] == "convencion"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code in (200, 400, 422), response.text
        data = response.json()
        # Supported decimal-comma convention must evaluate to 7/2. Otherwise
        # it must reject visibly; never silently return a different number.
        if response.status_code == 200:
            MathResponse.model_validate(data)
            if data["success"]:
                assert sympy.sympify(data["result_text"]) == sympy.Rational(7, 2), data
                assert data["result_approx"] == pytest.approx(3.5), data
                assert data["error_code"] is None, data
            else:
                assert data["error_code"] and data["error_message"], data
        else:
            assert data.get("detail"), data
        recovery = client.post("/api/v1/evaluate", json={"expression": "1.5+2"})
        assert recovery.status_code == 200, recovery.text
        recovered = recovery.json()
        MathResponse.model_validate(recovered)
        assert recovered["success"] is True, recovered
        assert recovered["result_approx"] == pytest.approx(3.5), recovered


def test_syn30_thousands_grouping_explicit_http_translation_and_recovery():
    row = ROWS["SY-N-30"]
    assert row["entrada"] == "1{,}000+1"
    assert row["operacion"] == "convencion"
    # The frontend rejects ambiguous original punctuation without a locale.
    # This backend probe checks the explicitly ungrouped value, not MathLive conversion.
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "1000+1"})
        assert response.status_code == 200, response.text
        value = response.json()
        MathResponse.model_validate(value)
        assert value["success"] is True, value
        assert sympy.sympify(value["result_text"]) == sympy.Integer(1001), value
        assert value["result_approx"] == pytest.approx(1001), value
        assert value["error_code"] is None, value
        reentry = client.post("/api/v1/evaluate", json={"expression": value["result_text"]})
        assert reentry.status_code == 200, reentry.text
        repeated = reentry.json()
        MathResponse.model_validate(repeated)
        assert repeated["success"] is True, repeated
        assert repeated["request_id"] != value["request_id"], repeated
        assert sympy.sympify(repeated["result_text"]) == sympy.Integer(1001), repeated


def test_syn31_small_rational_scientific_value_and_http_reentry():
    row = ROWS["SY-N-31"]
    assert row["entrada"] == r"\frac{1}{3000000}"
    assert row["esperado"] == r"3.333333333\times10^{-7}"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "1/3000000"})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert sympy.sympify(data["result_text"]) == sympy.Rational(1, 3000000), data
        assert data["result_approx"] == pytest.approx(1 / 3000000, rel=1e-9), data
        assert data["error_code"] is None, data
        repeated = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert repeated.status_code == 200, repeated.text
        again = repeated.json()
        MathResponse.model_validate(again)
        assert again["success"] is True and again["request_id"] != data["request_id"], again
        assert sympy.sympify(again["result_text"]) == sympy.Rational(1, 3000000), again


def test_syd01_unclosed_parenthesis_http_rejected_without_silent_evaluation():
    row = ROWS["SY-D-01"]
    assert row["entrada"] == "(2+3"
    assert row["operacion"] == "error"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code in (200, 400, 422), response.text
        data = response.json()
        if response.status_code == 200:
            MathResponse.model_validate(data)
            assert data["success"] is False, data
            assert data["error_code"] in {"PARSE_ERROR", "VALIDATION_ERROR"}, data
            assert data["error_message"], data
        else:
            assert data.get("detail") or data.get("error_message"), data
        assert "result_text" not in data or data["result_text"] not in ("5", 5), data


def test_syd02_extra_closing_parenthesis_http_is_explicit_error():
    row = ROWS["SY-D-02"]
    assert row["entrada"] == "2+3)"
    assert row["operacion"] == "error"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code in (200, 400, 422), response.text
        data = response.json()
        if response.status_code == 200:
            MathResponse.model_validate(data)
            assert data["success"] is False, data
            assert data["error_code"] in {"PARSE_ERROR", "VALIDATION_ERROR"}, data
            assert data["error_message"], data
        else:
            assert data.get("detail") or data.get("error_message"), data
        assert data.get("result_text") not in ("5", 5), data


def test_syd03_empty_parentheses_http_is_explicit_error():
    row = ROWS["SY-D-03"]
    assert row["entrada"] == "()"
    assert row["operacion"] == "error"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code in (200, 400, 422), response.text
        data = response.json()
        if response.status_code == 200:
            MathResponse.model_validate(data)
            assert data["success"] is False, data
            assert data["error_code"] in {"PARSE_ERROR", "VALIDATION_ERROR"}, data
            assert data["error_message"], data
        else:
            assert data.get("detail") or data.get("error_message"), data
        assert data.get("result_text") not in ("0", "1", 0, 1), data


def test_syd04_mismatched_parenthesis_bracket_http_explicit_error():
    row = ROWS["SY-D-04"]
    assert row["entrada"] == "(1+2]"
    assert row["operacion"] == "error"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code in (200, 400, 422), response.text
        data = response.json()
        if response.status_code == 200:
            MathResponse.model_validate(data)
            assert data["success"] is False, data
            assert data["error_code"] in {"PARSE_ERROR", "VALIDATION_ERROR"}, data
            assert data["error_message"], data
        else:
            assert data.get("detail") or data.get("error_message"), data
        assert data.get("result_text") not in ("3", 3), data


def test_syd05_mismatched_latex_left_right_delimiters_explicit_error():
    row = ROWS["SY-D-05"]
    assert row["entrada"] == r"\left(1+2\right]"
    assert row["operacion"] == "error"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code in (200, 400, 422), response.text
        data = response.json()
        if response.status_code == 200:
            MathResponse.model_validate(data)
            assert data["success"] is False, data
            assert data["error_code"] in {"PARSE_ERROR", "VALIDATION_ERROR"}, data
            assert data["error_message"], data
        else:
            assert data.get("detail") or data.get("error_message"), data
        assert data.get("result_text") not in ("3", 3), data


def test_syd06_square_bracketed_sum_normalized_http_and_reentry():
    row = ROWS["SY-D-06"]
    assert row["entrada"] == r"[1+2]\cdot3"
    assert row["operacion"] == "valor"
    assert row["esperado"] == "9"
    # Plus HTTP accepts normalized expression; frontend MathLive conversion is not asserted here.
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "(1+2)*3"})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert sympy.sympify(data["result_text"]) == sympy.Integer(9), data
        assert data["result_approx"] == pytest.approx(9), data
        assert data["error_code"] is None, data
        again_response = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert again_response.status_code == 200, again_response.text
        again = again_response.json()
        MathResponse.model_validate(again)
        assert again["success"] is True and again["request_id"] != data["request_id"], again
        assert sympy.sympify(again["result_text"]) == sympy.Integer(9), again

def test_syd07_braces_group_or_set_requires_explicit_convention():
    row = ROWS["SY-D-07"]
    assert row["entrada"] == r"\{1+2\}\cdot3"
    assert row["operacion"] == "convencion"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code in (200, 400, 422), response.text
        data = response.json()
        if response.status_code == 200:
            MathResponse.model_validate(data)
            if data["success"]:
                assert sympy.sympify(data["result_text"]) == sympy.Integer(9), data
            else:
                assert data["error_code"] in {"PARSE_ERROR", "VALIDATION_ERROR"}, data
                assert data["error_message"], data
        else:
            assert data.get("detail") or data.get("error_message"), data

def test_syd08_parenthesized_power_normalized_http_and_reentry():
    row = ROWS["SY-D-08"]
    assert row["entrada"] == r"\left(1+2\right)^{2}"
    assert row["operacion"] == "valor"
    assert row["esperado"] == "9"
    # Plus HTTP receives normalized expression, not a MathLive browser event.
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "(1+2)**2"})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert sympy.sympify(data["result_text"]) == sympy.Integer(9), data
        assert data["result_approx"] == pytest.approx(9), data
        assert data["error_code"] is None, data
        reentry = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert reentry.status_code == 200, reentry.text
        again = reentry.json()
        MathResponse.model_validate(again)
        assert again["success"] is True, again
        assert sympy.sympify(again["result_text"]) == sympy.Integer(9), again

def test_syd09_parenthesized_fraction_power_exact_http_and_reentry():
    row = ROWS["SY-D-09"]
    assert row["entrada"] == r"\left(\frac{1}{2}\right)^{2}"
    assert row["operacion"] == "valor"
    assert row["esperado"] == r"\frac{1}{4}"
    # HTTP normalized math; MathLive-to-HTTP conversion is not evidenced by this test.
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "(1/2)**2"})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert sympy.sympify(data["result_text"]) == sympy.Rational(1, 4), data
        assert data["result_approx"] == pytest.approx(0.25), data
        assert data["error_code"] is None, data
        repeat = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert repeat.status_code == 200, repeat.text
        again = repeat.json()
        MathResponse.model_validate(again)
        assert again["success"] is True, again
        assert sympy.sympify(again["result_text"]) == sympy.Rational(1, 4), again

def test_syd10_adjacent_parentheses_implicit_product_http_and_reentry():
    row = ROWS["SY-D-10"]
    assert row["entrada"] == "(1+2)(3+4)"
    assert row["operacion"] == "valor"
    assert row["esperado"] == "21"
    # Direct HTTP input probes backend implicit multiplication, not MathLive editor.
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert sympy.sympify(data["result_text"]) == sympy.Integer(21), data
        assert data["result_approx"] == pytest.approx(21), data
        assert data["error_code"] is None, data
        repeat = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert repeat.status_code == 200, repeat.text
        again = repeat.json()
        MathResponse.model_validate(again)
        assert again["success"] is True, again
        assert sympy.sympify(again["result_text"]) == sympy.Integer(21), again

def test_syd11_parenthesis_followed_by_number_implicit_product_http_reentry():
    row = ROWS["SY-D-11"]
    assert row["entrada"] == "(1+2)3"
    assert row["operacion"] == "valor"
    assert row["esperado"] == "9"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert sympy.sympify(data["result_text"]) == sympy.Integer(9), data
        assert data["result_approx"] == pytest.approx(9), data
        assert data["error_code"] is None, data
        repeated = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert repeated.status_code == 200, repeated.text
        again = repeated.json()
        MathResponse.model_validate(again)
        assert again["success"] is True, again
        assert sympy.sympify(again["result_text"]) == sympy.Integer(9), again

def test_syd12_numeric_factor_before_parentheses_implicit_product_http_reentry():
    row = ROWS["SY-D-12"]
    assert row["entrada"] == "3(1+2)"
    assert row["operacion"] == "valor"
    assert row["esperado"] == "9"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert sympy.sympify(data["result_text"]) == sympy.Integer(9), data
        assert data["result_approx"] == pytest.approx(9), data
        assert data["error_code"] is None, data
        repeated = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert repeated.status_code == 200, repeated.text
        again = repeated.json()
        MathResponse.model_validate(again)
        assert again["success"] is True, again
        assert sympy.sympify(again["result_text"]) == sympy.Integer(9), again

def test_syd13_ten_nested_parentheses_exact_http_and_reentry():
    row = ROWS["SY-D-13"]
    assert row["entrada"] == "(" * 10 + "1" + ")" * 10
    assert row["esperado"] == "1"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert sympy.sympify(data["result_text"]) == sympy.Integer(1), data
        assert data["error_code"] is None, data
        second = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert second.status_code == 200, second.text
        again = second.json()
        MathResponse.model_validate(again)
        assert again["success"] is True, again
        assert sympy.sympify(again["result_text"]) == sympy.Integer(1), again

def test_syd14_double_parentheses_exact_http_and_reentry():
    row = ROWS["SY-D-14"]
    assert row["entrada"] == "((2))"
    assert row["operacion"] == "valor"
    assert row["esperado"] == "2"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert sympy.sympify(data["result_text"]) == sympy.Integer(2), data
        assert data["error_code"] is None, data
        repeated = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert repeated.status_code == 200, repeated.text
        again = repeated.json()
        MathResponse.model_validate(again)
        assert again["success"] is True, again
        assert sympy.sympify(again["result_text"]) == sympy.Integer(2), again


def test_syu01_original_multiplication_translation_http_and_reentry():
    row = ROWS["SY-U-01"]
    assert row["entrada"] == r"3\times4"
    assert row["operacion"] == "valor"
    assert row["esperado"] == "12"
    # Original LaTeX conversion has an independent frontend test.
    expression = "3*4"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert data["operation"] == "evaluate" and data["result_type"] == "scalar", data
        assert data["input_text"] == expression and data["request_id"], data
        assert data["result_text"] == "12" and data["result_latex"] == "12", data
        assert data["result_approx"] == 12, data
        assert data["error_code"] is None and data["error_message"] is None, data
        response2 = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert response2.status_code == 200, response2.text
        again = response2.json()
        MathResponse.model_validate(again)
        assert again["success"] is True, again
        assert again["request_id"] != data["request_id"], again
        assert again["result_text"] == "12" and again["result_approx"] == 12, again


def test_syu02_original_division_translation_http_and_reentry():
    row = ROWS["SY-U-02"]
    assert row["entrada"] == r"12\div4"
    assert row["operacion"] == "valor"
    assert row["esperado"] == "3"
    # Original LaTeX conversion has an independent frontend test.
    expression = "12/4"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert data["operation"] == "evaluate" and data["result_type"] == "scalar", data
        assert data["input_text"] == expression and data["request_id"], data
        assert data["result_text"] == "3" and data["result_latex"] == "3", data
        assert data["result_approx"] == 3, data
        assert data["error_code"] is None and data["error_message"] is None, data
        response2 = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert response2.status_code == 200, response2.text
        again = response2.json()
        MathResponse.model_validate(again)
        assert again["success"] is True, again
        assert again["request_id"] != data["request_id"], again
        assert again["result_text"] == "3" and again["result_approx"] == 3, again


def test_syu03_original_cdot_translation_http_and_reentry():
    row = ROWS["SY-U-03"]
    assert row["entrada"] == r"3\cdot4"
    assert row["operacion"] == "valor"
    assert row["esperado"] == "12"
    # Original LaTeX conversion has an independent frontend test.
    expression = "3*4"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert data["operation"] == "evaluate" and data["result_type"] == "scalar", data
        assert data["input_text"] == expression and data["request_id"], data
        assert data["result_text"] == "12" and data["result_latex"] == "12", data
        assert data["result_approx"] == 12, data
        assert data["error_code"] is None and data["error_message"] is None, data
        response2 = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert response2.status_code == 200, response2.text
        again = response2.json()
        MathResponse.model_validate(again)
        assert again["success"] is True, again
        assert again["request_id"] != data["request_id"], again
        assert again["result_text"] == "12" and again["result_approx"] == 12, again



def test_syu04_ascii_multiplication_http_and_reentry():
    row = ROWS["SY-U-04"]
    assert row["entrada"] == "3*4"
    assert row["operacion"] == "valor"
    assert row["esperado"] == "12"
    expression = row["entrada"]
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert data["operation"] == "evaluate" and data["result_type"] == "scalar", data
        assert data["input_text"] == expression and data["request_id"], data
        assert data["result_text"] == "12" and data["result_latex"] == "12", data
        assert data["result_approx"] == 12, data
        assert data["error_code"] is None and data["error_message"] is None, data
        response2 = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert response2.status_code == 200, response2.text
        again = response2.json()
        MathResponse.model_validate(again)
        assert again["success"] is True, again
        assert again["request_id"] != data["request_id"], again
        assert again["result_text"] == "12" and again["result_approx"] == 12, again

def test_syu05_ascii_division_http_and_reentry():
    row = ROWS["SY-U-05"]
    assert row["entrada"] == "12/4"
    assert row["operacion"] == "valor"
    assert row["esperado"] == "3"
    expression = row["entrada"]
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert data["operation"] == "evaluate" and data["result_type"] == "scalar", data
        assert data["input_text"] == expression and data["request_id"], data
        assert data["result_text"] == "3" and data["result_latex"] == "3", data
        assert data["result_approx"] == 3, data
        assert data["error_code"] is None and data["error_message"] is None, data
        response2 = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert response2.status_code == 200, response2.text
        again = response2.json()
        MathResponse.model_validate(again)
        assert again["success"] is True, again
        assert again["request_id"] != data["request_id"], again
        assert again["result_text"] == "3" and again["result_approx"] == 3, again


def test_syu06_unicode_multiplication_http_and_reentry():
    row = ROWS["SY-U-06"]
    assert row["entrada"] == "3×4"
    assert row["operacion"] == "valor"
    assert row["esperado"] == "12"
    # HTTP receives original Unicode source; translation must not be assumed.
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert data["result_text"] == "12" and data["result_approx"] == 12, data
        assert data["error_code"] is None, data
        second = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert second.status_code == 200, second.text
        again = second.json()
        MathResponse.model_validate(again)
        assert again["success"] is True and again["result_text"] == "12", again
        assert again["request_id"] != data["request_id"], again


def test_syu07_unicode_division_http_and_reentry():
    row = ROWS["SY-U-07"]
    assert row["entrada"] == "12÷4"
    assert row["operacion"] == "valor"
    assert row["esperado"] == "3"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert data["result_text"] == "3" and data["result_latex"] == "3", data
        assert data["result_approx"] == 3 and data["error_code"] is None, data
        repeated = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert repeated.status_code == 200, repeated.text
        again = repeated.json()
        MathResponse.model_validate(again)
        assert again["success"] is True and again["result_text"] == "3", again
        assert again["request_id"] != data["request_id"], again


def test_syu08_unicode_middle_dot_http_and_reentry():
    row = ROWS["SY-U-08"]
    assert row["entrada"] == "3·4"
    assert row["operacion"] == "valor"
    assert row["esperado"] == "12"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert data["result_text"] == "12" and data["result_latex"] == "12", data
        assert data["result_approx"] == 12 and data["error_code"] is None, data
        repeated = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert repeated.status_code == 200, repeated.text
        again = repeated.json()
        MathResponse.model_validate(again)
        assert again["success"] is True and again["result_text"] == "12", again
        assert again["request_id"] != data["request_id"], again


def test_syu09_unicode_minus_http_and_reentry():
    row = ROWS["SY-U-09"]
    assert row["entrada"] == "2−1"
    assert row["operacion"] == "valor"
    assert row["esperado"] == "1"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert data["result_text"] == "1" and data["result_latex"] == "1", data
        assert data["result_approx"] == 1 and data["error_code"] is None, data
        repeated = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert repeated.status_code == 200, repeated.text
        again = repeated.json()
        MathResponse.model_validate(again)
        assert again["success"] is True and again["result_text"] == "1", again
        assert again["request_id"] != data["request_id"], again


def test_syu10_en_dash_convention_http():
    row = ROWS["SY-U-10"]
    assert row["entrada"] == "2–1"
    assert row["operacion"] == "convencion"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        data = response.json()
        MathResponse.model_validate(data)
        if data["success"]:
            assert data["result_text"] == "1" and data["result_approx"] == 1, data
            assert data["error_code"] is None, data
            repeated = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
            assert repeated.status_code == 200 and repeated.json()["result_text"] == "1"
        else:
            assert data["error_code"] is not None and data["error_message"], data


def test_syu11_unicode_superscript_convention_http():
    row = ROWS["SY-U-11"]
    assert row["entrada"] == "x²"
    assert row["operacion"] == "convencion"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        data = response.json()
        MathResponse.model_validate(data)
        if data["success"]:
            x = sympy.Symbol("x")
            assert sympy.simplify(sympy.sympify(data["result_text"]) - x**2) == 0, data
            repeated = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
            assert repeated.status_code == 200, repeated.text
            assert repeated.json()["success"] is True, repeated.json()
        else:
            assert data["error_code"] is not None and data["error_message"], data


def test_syu12_unicode_square_root_convention_http():
    row = ROWS["SY-U-12"]
    assert row["entrada"] == "√4"
    assert row["operacion"] == "convencion"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        data = response.json()
        MathResponse.model_validate(data)
        if data["success"]:
            assert sympy.sympify(data["result_text"]) == 2, data
            assert data["result_approx"] == 2, data
            repeated = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
            assert repeated.status_code == 200 and repeated.json()["success"] is True
            assert sympy.sympify(repeated.json()["result_text"]) == 2
        else:
            assert data["error_code"] is not None and data["error_message"], data


def test_syu13_unicode_pi_http_precision_and_reentry():
    row = ROWS["SY-U-13"]
    assert row["entrada"] == "π"
    assert row["operacion"] == "valor"
    assert row["esperado"] == "3.141592654"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert data["error_code"] is None, data
        assert round(float(data["result_approx"]), 9) == float(row["esperado"]), data
        repeated = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert repeated.status_code == 200, repeated.text
        again = repeated.json()
        MathResponse.model_validate(again)
        assert again["success"] is True, again
        assert round(float(again["result_approx"]), 9) == float(row["esperado"]), again
        assert again["request_id"] != data["request_id"]


def test_syu14_thin_latex_spaces_http_and_reentry():
    row = ROWS["SY-U-14"]
    assert row["entrada"] == r"3\,+\,4"
    assert row["operacion"] == "valor"
    assert row["esperado"] == "7"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert sympy.sympify(data["result_text"]) == 7, data
        assert data["result_approx"] == 7 and data["error_code"] is None, data
        repeated = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert repeated.status_code == 200, repeated.text
        again = repeated.json()
        MathResponse.model_validate(again)
        assert again["success"] is True and sympy.sympify(again["result_text"]) == 7
        assert again["request_id"] != data["request_id"]


def test_syu15_medium_latex_spaces_http_and_reentry():
    row = ROWS["SY-U-15"]
    assert row["entrada"] == r"3\;+\;4"
    assert row["operacion"] == "valor"
    assert row["esperado"] == "7"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert sympy.sympify(data["result_text"]) == 7, data
        assert data["result_approx"] == 7 and data["error_code"] is None, data
        repeated = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert repeated.status_code == 200, repeated.text
        again = repeated.json()
        MathResponse.model_validate(again)
        assert again["success"] is True and sympy.sympify(again["result_text"]) == 7
        assert again["request_id"] != data["request_id"]


def test_syu16_nonbreaking_spaces_http_and_reentry():
    row = ROWS["SY-U-16"]
    assert row["esperado"] == "7"
    assert "U+00A0" in row["nota"]
    source = "3\u00a0+\u00a04"
    assert row["entrada"].replace(" ", "\u00a0") == source
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": source})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert sympy.sympify(data["result_text"]) == 7, data
        assert data["result_approx"] == 7 and data["error_code"] is None, data
        repeated = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert repeated.status_code == 200, repeated.text
        again = repeated.json()
        MathResponse.model_validate(again)
        assert again["success"] is True and sympy.sympify(again["result_text"]) == 7


def test_syu17_fullwidth_digits_and_plus_http_reentry():
    row = ROWS["SY-U-17"]
    assert row["entrada"] == "２＋３"
    assert row["esperado"] == "5"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert sympy.sympify(data["result_text"]) == 5, data
        assert data["result_approx"] == 5 and data["error_code"] is None, data
        repeated = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert repeated.status_code == 200, repeated.text
        again = repeated.json()
        MathResponse.model_validate(again)
        assert again["success"] is True and sympy.sympify(again["result_text"]) == 5


def test_syu18_consecutive_plus_minus_http_and_reentry():
    row = ROWS["SY-U-18"]
    assert row["entrada"] == "2+-3"
    assert row["operacion"] == "valor"
    assert row["esperado"] == "-1"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert sympy.sympify(data["result_text"]) == -1, data
        assert data["result_approx"] == -1 and data["error_code"] is None, data
        repeated = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert repeated.status_code == 200, repeated.text
        again = repeated.json()
        MathResponse.model_validate(again)
        assert again["success"] is True and sympy.sympify(again["result_text"]) == -1


def test_syu19_consecutive_minus_operators_http_and_reentry():
    row = ROWS["SY-U-19"]
    assert row["entrada"] == "2--3"
    assert row["operacion"] == "valor"
    assert row["esperado"] == "5"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert sympy.sympify(data["result_text"]) == 5, data
        assert data["result_approx"] == 5 and data["error_code"] is None, data
        repeated = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert repeated.status_code == 200, repeated.text
        again = repeated.json()
        MathResponse.model_validate(again)
        assert again["success"] is True and sympy.sympify(again["result_text"]) == 5
        assert again["request_id"] != data["request_id"]


def test_syu20_multiplication_negative_operand_http_and_reentry():
    row = ROWS["SY-U-20"]
    assert row["entrada"] == "2*-3"
    assert row["operacion"] == "valor"
    assert row["esperado"] == "-6"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert sympy.sympify(data["result_text"]) == -6, data
        assert data["result_approx"] == -6 and data["error_code"] is None, data
        repeated = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert repeated.status_code == 200, repeated.text
        again = repeated.json()
        MathResponse.model_validate(again)
        assert again["success"] is True and sympy.sympify(again["result_text"]) == -6
        assert again["request_id"] != data["request_id"]


def test_syu21_leading_double_unary_minus_http_and_reentry():
    row = ROWS["SY-U-21"]
    assert row["entrada"] == "--3"
    assert row["operacion"] == "valor"
    assert row["esperado"] == "3"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert sympy.sympify(data["result_text"]) == 3, data
        assert data["result_approx"] == 3 and data["error_code"] is None, data
        repeated = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert repeated.status_code == 200, repeated.text
        again = repeated.json()
        MathResponse.model_validate(again)
        assert again["success"] is True and sympy.sympify(again["result_text"]) == 3
        assert again["request_id"] != data["request_id"]


def test_syu22_incomplete_trailing_operator_http_error():
    row = ROWS["SY-U-22"]
    assert row["entrada"] == "2+"
    assert row["operacion"] == "error"
    assert "expresión incompleta" in row["esperado"]
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code in (200, 400, 422), response.text
        data = response.json()
        if response.status_code == 200:
            MathResponse.model_validate(data)
            assert data["success"] is False, data
            assert data["error_code"] in {"PARSE_ERROR", "VALIDATION_ERROR"}, data
            assert data["error_message"], data
            message = str(data["error_message"])
            assert any(t in message.lower() for t in ("incomplet", "oper", "syntax", "sintax", "expres", "unexpected"))
        else:
            assert data.get("detail") or data.get("error_message"), data
        assert data.get("result_text") not in ("2", 2), data


def test_syu23_leading_multiplication_operator_http_error():
    row = ROWS["SY-U-23"]
    assert row["entrada"] == "*2"
    assert row["operacion"] == "error"
    assert "operador sin operando" in row["esperado"]
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code in (200, 400, 422), response.text
        data = response.json()
        if response.status_code == 200:
            MathResponse.model_validate(data)
            assert data["success"] is False, data
            assert data["error_code"] in {"PARSE_ERROR", "VALIDATION_ERROR"}, data
            assert data["error_message"], data
            assert any(t in str(data["error_message"]).lower() for t in ("oper", "operand", "syntax", "sintax", "expres", "unexpected")), data
        else:
            assert data.get("detail") or data.get("error_message"), data
        assert data.get("result_text") not in ("2", 2), data


def test_syu24_spaced_numerals_declared_convention_http():
    row = ROWS["SY-U-24"]
    assert row["entrada"] == r"2\ 3"
    assert row["operacion"] == "convencion"
    assert "Dos números separados por espacio" in row["nota"]
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code in (200, 400, 422), response.text
        data = response.json()
        if response.status_code == 200:
            MathResponse.model_validate(data)
            if data["success"]:
                value = sympy.sympify(data["result_text"])
                assert value in (6, 23), data
                repeated = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
                assert repeated.status_code == 200, repeated.text
                again = repeated.json()
                MathResponse.model_validate(again)
                assert again["success"] is True and sympy.sympify(again["result_text"]) == value, again
            else:
                assert data["error_code"] in {"PARSE_ERROR", "VALIDATION_ERROR"}, data
                assert data["error_message"], data
        else:
            assert data.get("detail") or data.get("error_message"), data


def test_syu25_consecutive_plus_convention_http():
    row = ROWS["SY-U-25"]
    assert row["entrada"] == "2++3"
    assert row["operacion"] == "convencion"
    assert "5" in row["esperado"]
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code in (200, 400, 422), response.text
        data = response.json()
        if response.status_code == 200:
            MathResponse.model_validate(data)
            if data["success"]:
                assert sympy.sympify(data["result_text"]) == 5, data
                assert data["result_approx"] == 5, data
                repeated = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
                assert repeated.status_code == 200, repeated.text
                again = repeated.json()
                MathResponse.model_validate(again)
                assert again["success"] is True and sympy.sympify(again["result_text"]) == 5, again
            else:
                assert data["error_code"] in {"PARSE_ERROR", "VALIDATION_ERROR"}, data
                assert data["error_message"], data
        else:
            assert data.get("detail") or data.get("error_message"), data


def test_syv01_uppercase_and_lowercase_remain_independent_http_reentry():
    row = ROWS["SY-V-01"]
    assert row["entrada"] == "X+x"
    assert row["operacion"] == "interpretacion"
    assert row["esperado"] == "X+x"
    X, x = sympy.symbols("X x")
    expected = X + x
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        result = sympy.sympify(data["result_text"])
        assert sympy.simplify(result - expected) == 0, data
        assert result.free_symbols == {X, x}, data
        repeated = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert repeated.status_code == 200, repeated.text
        again = repeated.json()
        MathResponse.model_validate(again)
        assert again["success"] is True, again
        assert sympy.sympify(again["result_text"]).free_symbols == {X, x}, again


def test_syv02_distinct_subscripted_variables_http_and_reentry():
    row = ROWS["SY-V-02"]
    assert row["entrada"] == r"x_{1}+x_{2}"
    assert row["operacion"] == "interpretacion"
    assert row["esperado"] == r"x_{1}+x_{2}"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        result = sympy.sympify(data["result_text"])
        assert len(result.free_symbols) == 2, data
        names = {str(s) for s in result.free_symbols}
        assert len(names) == 2 and all("1" in name or "2" in name for name in names), data
        repeated = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert repeated.status_code == 200, repeated.text
        again = repeated.json()
        MathResponse.model_validate(again)
        assert again["success"] is True, again
        assert {str(s) for s in sympy.sympify(again["result_text"]).free_symbols} == names, again
