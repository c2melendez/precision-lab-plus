"""Regression sentinels for defects found by Track D (M1-M15)."""

import os

os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def evaluate(expression: str):
    return client.post("/api/v1/evaluate", json={"expression": expression}).json()


@pytest.mark.parametrize("expression", ["csc(0)", "cot(0)", "asech(0)"])
def test_m1_singularities_are_domain_errors(expression: str):
    body = evaluate(expression)
    assert body["success"] is False
    assert body["error_code"] == "DOMAIN_ERROR"


@pytest.mark.parametrize("expression", ["foo(x)", "dsolve(x)"])
def test_m4_m13_unknown_function_calls_are_rejected(expression: str):
    body = evaluate(expression)
    assert body["success"] is False
    assert body["error_code"] == "PARSE_ERROR"


def test_m13_internal_sympy_exception_name_is_not_exposed():
    body = evaluate("Matrix([[1,2],[3,4]])")
    assert body["success"] is False
    assert body["error_code"] == "PARSE_ERROR"
    assert "SympifyError" not in (body["error_message"] or "")


def test_m10_percent_is_postfix_division_by_100():
    body = evaluate("50%")
    assert body["success"] is True
    assert body["result_approx"] == pytest.approx(0.5)


def test_m10_plus_minus_keeps_both_branches():
    body = evaluate("pm(5)")
    assert body["success"] is True
    assert body["result_text"] == "{-5, 5}"


def test_m3_productoria_is_enabled():
    body = evaluate("product(i,i,1,5)")
    assert body["success"] is True
    assert body["result_approx"] == pytest.approx(120.0)


def test_m3_sum_still_works_after_aggregate_guard():
    body = evaluate("sum(i,i,1,5)")
    assert body["success"] is True
    assert body["result_approx"] == pytest.approx(15.0)


def test_m5_complex_log_uses_natural_principal_branch():
    body = evaluate("Log(-1)")
    assert body["success"] is True
    assert body["result_text"] == "I*pi"


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("acsc(2)", 0.5235987755982989),
        ("asec(2)", 1.0471975511965979),
        ("acot(1)", 0.7853981633974483),
        ("csch(1)", 0.8509181282393216),
        ("sech(0)", 1.0),
        ("coth(1)", 1.3130352854993312),
    ],
)
def test_m10_active_functions_are_functions_not_symbols(expression: str, expected: float):
    body = evaluate(expression)
    assert body["success"] is True
    assert body["result_approx"] == pytest.approx(expected)


def test_m3_bilateral_limit_reports_dne():
    body = client.post(
        "/api/v1/limit",
        json={"expression": "1/x", "variable": "x", "point": "0", "direction": "both"},
    ).json()
    assert body["success"] is True
    assert body["result_text"] == "DNE"
