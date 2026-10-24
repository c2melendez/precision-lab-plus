"""SY-E-17: declared default principal complex branch through Plus HTTP."""
import json
import math
import os
from pathlib import Path
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
import pytest
import sympy
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.responses import MathResponse

DATA = Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl"
ROWS = {r["id"]: r for r in (json.loads(line) for line in DATA.read_text(encoding="utf-8").splitlines() if line.strip())}

def test_sye17_default_principal_complex_power_http_and_response():
    row = ROWS["SY-E-17"]
    assert row["operacion"] == "convencion"
    assert row["entrada"] == "(-2)^{0.5}"
    assert "ℂ" in row["esperado"]
    expression = "(-2)^0.5"  # Explicit backend translation; original MathLive UI is separate.
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
    assert response.status_code == 200, response.text
    data = response.json()
    MathResponse.model_validate(data)
    assert data["success"] is True, data
    assert data["operation"] == "evaluate", data
    assert data["request_id"], data
    assert data["result_type"] == "scalar", data
    assert data["input_text"] == expression, data
    assert data["result_approx"] is None, data
    assert data["error_code"] is None and data["error_message"] is None, data
    assert isinstance(data["steps"], list) and isinstance(data["warnings"], list), data
    assert isinstance(data["has_detailed_steps"], bool), data
    assert math.isfinite(data["duration_ms"]) and data["duration_ms"] >= 0, data
    assert isinstance(data["result_latex"], str) and "i" in data["result_latex"], data
    assert isinstance(data["result_text"], str) and "I" in data["result_text"], data
    # Only parse returned notation; expected coordinates are independent constants.
    represented = sympy.sympify(data["result_text"], locals={"I": sympy.I, "sqrt": sympy.sqrt})
    assert not represented.free_symbols, data
    actual = complex(represented.evalf(17))
    assert math.isfinite(actual.real) and math.isfinite(actual.imag), data
    assert actual.real == pytest.approx(0, abs=1e-12), data
    assert actual.imag > 0, data
    assert actual.imag == pytest.approx(1.4142135623730951, rel=1e-12, abs=1e-12), data
    squared = actual * actual
    assert squared.real == pytest.approx(-2, abs=1e-12), data
    assert squared.imag == pytest.approx(0, abs=1e-12), data


def test_sye18_original_cube_root_power_principal_complex_http():
    row = ROWS["SY-E-18"]
    assert row["operacion"] == "convencion"
    assert row["entrada"] == r"(-8)^{\frac{1}{3}}"
    assert "declarar" in row["nota"]
    expression = "(-8)^(1/3)"  # Same original power, not cbrt()/root().
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
    assert response.status_code == 200, response.text
    data = response.json()
    MathResponse.model_validate(data)
    assert data["success"] is True, data
    assert data["operation"] == "evaluate" and data["result_type"] == "scalar", data
    assert data["request_id"] and data["input_text"] == expression, data
    assert data["result_approx"] is None, data
    assert data["error_code"] is None and data["error_message"] is None, data
    assert isinstance(data["result_text"], str) and data["result_text"], data
    assert isinstance(data["result_latex"], str) and data["result_latex"], data
    assert math.isfinite(data["duration_ms"]) and data["duration_ms"] >= 0, data
    # A principal-power expression is valid exact notation even before expansion into a+bI.
    represented = sympy.sympify(data["result_text"], locals={"I": sympy.I, "sqrt": sympy.sqrt})
    assert not represented.free_symbols, data
    actual = complex(represented.evalf(17))
    assert math.isfinite(actual.real) and math.isfinite(actual.imag), data
    assert actual.real == pytest.approx(1, rel=1e-12, abs=1e-12), data
    assert actual.imag > 0, data
    assert actual.imag == pytest.approx(1.7320508075688772, rel=1e-12, abs=1e-12), data
    cubed = actual * actual * actual
    assert cubed.real == pytest.approx(-8, abs=1e-12), data
    assert cubed.imag == pytest.approx(0, abs=1e-12), data


def test_sye19_declared_zero_to_zero_convention_http():
    row = ROWS["SY-E-19"]
    assert row["operacion"] == "convencion"
    assert row["entrada"] == "0^{0}"
    assert "convención declarada" in row["esperado"]
    expression = "0^0"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
    assert response.status_code == 200, response.text
    data = response.json()
    MathResponse.model_validate(data)
    assert data["success"] is True, data
    assert data["operation"] == "evaluate" and data["result_type"] == "scalar", data
    assert data["input_text"] == expression and data["request_id"], data
    assert data["result_text"] == "1" and data["result_latex"] == "1", data
    assert data["result_approx"] == 1, data
    assert data["error_code"] is None and data["error_message"] is None, data

def test_sye20_zero_negative_power_clear_domain_error_and_recovery_http():
    row = ROWS["SY-E-20"]
    assert row["operacion"] == "error"
    assert row["entrada"] == "0^{-1}"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": "0^(-1)"})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is False, data
        assert data["operation"] == "evaluate" and data["request_id"], data
        assert data["error_code"] == "DOMAIN_ERROR", data
        assert any(word in data["error_message"].lower() for word in ("cero", "zero", "divisi")), data
        assert data["result_approx"] is None, data
        assert data["result_text"] is None and data["result_latex"] is None, data
        recovery = client.post("/api/v1/evaluate", json={"expression": "2+3"})
        assert recovery.status_code == 200, recovery.text
        recovered = recovery.json()
        assert recovered["success"] is True and recovered["result_approx"] == 5, recovered
        assert recovered["request_id"] != data["request_id"], (data, recovered)


@pytest.mark.parametrize("expression", ["0^(-2)", "1/0"])
def test_sye20_related_zero_denominators_have_specific_domain_feedback(expression):
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is False and data["error_code"] == "DOMAIN_ERROR", data
    assert "cero" in data["error_message"].lower(), data
    assert data["result_approx"] is None, data

@pytest.mark.parametrize("expression, expected", [("0^1", 0), ("0^2", 0), ("2^(-1)", 0.5)])
def test_sye19_20_valid_power_controls_are_preserved(expression, expected):
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True, data
    assert data["result_approx"] == expected, data


def test_sye21_exact_half_http_response_and_actual_result_reentry():
    row = ROWS["SY-E-21"]
    assert row["operacion"] == "valor"
    assert row["entrada"] == r"\frac12"
    assert row["esperado"] == r"\frac{1}{2}"
    expression = "1/2"  # Explicit HTTP translation; original source conversion tested separately.
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        assert data["operation"] == "evaluate" and data["result_type"] == "scalar", data
        assert data["request_id"] and data["input_text"] == expression, data
        assert data["result_text"] == "1/2", data
        assert data["result_latex"] == r"\frac{1}{2}", data
        assert data["result_approx"] == 0.5, data
        assert data["error_code"] is None and data["error_message"] is None, data
        assert math.isfinite(data["duration_ms"]) and data["duration_ms"] >= 0, data
        reentry = client.post("/api/v1/evaluate", json={"expression": data["result_text"]})
        assert reentry.status_code == 200, reentry.text
        returned = reentry.json()
        MathResponse.model_validate(returned)
        assert returned["success"] is True, returned
        assert returned["request_id"] != data["request_id"], returned
        assert returned["result_text"] == "1/2" and returned["result_approx"] == 0.5, returned


def test_sye22_nested_fraction_symbolic_domain_and_substitutions_http():
    row = ROWS["SY-E-22"]
    assert row["entrada"] == r"\frac{1}{1+\frac{1}{x}}"
    expression = "1/(1+1/x)"  # Explicit translation; no native editor claim.
    x = sympy.Symbol("x")
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": expression})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True, data
        represented = sympy.sympify(data["result_text"])
        assert sympy.simplify(represented - x/(x+1)) == 0, data
        assert data["result_latex"] and data["result_approx"] is None, data
        conditions = [sympy.sympify(c["text"]) for c in data["domain_conditions"]]
        assert len(conditions) >= 2, data
        for value, expected in [(1, 0.5), (2, 2/3), (-2, 2)]:
            assert all(c.subs(x, value) == sympy.true for c in conditions), data
            sampled = client.post("/api/v1/evaluate", json={
                "expression": expression, "substitutions": {"x": str(value)},
            }).json()
            assert sampled["success"] is True, sampled
            assert sampled["result_approx"] == pytest.approx(expected), sampled
            reentry = client.post("/api/v1/evaluate", json={
                "expression": data["result_text"], "substitutions": {"x": str(value)},
            }).json()
            assert reentry["success"] is True, reentry
            assert reentry["result_approx"] == pytest.approx(expected), reentry
        for value in [0, -1]:
            # At least one original restriction explicitly excludes each point.
            assert any(c.subs(x, value) == sympy.false for c in conditions), data
            invalid_response = client.post("/api/v1/evaluate", json={
                "expression": expression, "substitutions": {"x": str(value)},
            })
            assert invalid_response.status_code == 200, invalid_response.text
            invalid = invalid_response.json()
            MathResponse.model_validate(invalid)
            assert invalid["success"] is False, invalid
            assert invalid["error_code"] == "DOMAIN_ERROR", invalid
            assert invalid["result_text"] is None and invalid["result_approx"] is None, invalid


@pytest.mark.parametrize("expression, substitutions", [
    ("1/(1+1/x)", {"x": "0"}),
    ("(x^2-1)/(x-1)", {"x": "1"}),
    ("1/(1+1/0)", None),
])
def test_sye22_original_zero_denominator_cannot_be_cancelled(expression, substitutions):
    with TestClient(app) as client:
        data = client.post("/api/v1/evaluate", json={
            "expression": expression, "substitutions": substitutions,
        }).json()
    assert data["success"] is False and data["error_code"] == "DOMAIN_ERROR", data
