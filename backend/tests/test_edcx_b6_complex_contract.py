"""EDCX-B6 VC-FE scalar complex contract tests (test-first).

These tests cover only scalar principal-branch cases. They do not certify
multivalued logarithms/powers, symbolic identities, or the full 53-row matrix.
The expected values come from Python's standard-library cmath, independently
of the product's SymPy evaluation path.
"""
import cmath
import math

import pytest
import sympy
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

CASES = [
    ("VC-FE-01", "exp(i*pi/2)", cmath.exp(1j * math.pi / 2)),
    ("VC-FE-02", "exp(-i*pi/4)", cmath.exp(-1j * math.pi / 4)),
    (
        "VC-FE-03",
        "exp(ln(2)+i*pi/3)",
        cmath.exp(math.log(2) + 1j * math.pi / 3),
    ),
    ("VC-FE-05", "Log(-1)", cmath.log(complex(-1, 0))),
    ("VC-FE-06", "Log(i)", cmath.log(1j)),
    ("VC-FE-07", "Log(1+i)", cmath.log(1 + 1j)),
    ("VC-FE-08", "Log(-1-i)", cmath.log(-1 - 1j)),
    ("VC-FE-09", "Log(3-3*i)", cmath.log(3 - 3j)),
    ("VC-FE-10", "Log(-e)", cmath.log(complex(-math.e, 0))),
]


def _decode_complex_result(result_text: str) -> complex:
    """Decode only the calculator's emitted SymPy-style scalar text."""
    expr = sympy.sympify(
        result_text.replace("^", "**"),
        locals={"I": sympy.I, "E": sympy.E, "ln": sympy.log},
    )
    value = complex(sympy.N(expr, 30))
    assert math.isfinite(value.real)
    assert math.isfinite(value.imag)
    return value


@pytest.mark.parametrize(
    ("case_id", "expression", "expected"),
    CASES,
    ids=[case[0] for case in CASES],
)
def test_edcx_b6_scalar_complex_values_match_independent_principal_oracle(
    case_id, expression, expected
):
    response = client.post("/api/v1/evaluate", json={"expression": expression})
    assert response.status_code == 200, f"{case_id}: {response.text}"

    body = response.json()
    assert body["success"] is True, f"{case_id}: {body}"
    assert body.get("error_code") is None, f"{case_id}: {body}"
    assert isinstance(body.get("result_text"), str) and body["result_text"], (
        f"{case_id}: missing scalar result_text: {body}"
    )
    assert isinstance(body.get("result_latex"), str) and body["result_latex"], (
        f"{case_id}: missing result_latex: {body}"
    )
    # Complex results are not represented by the real-only result_approx field.
    assert body.get("result_approx") is None, f"{case_id}: {body}"

    actual = _decode_complex_result(body["result_text"])
    assert actual.real == pytest.approx(expected.real, rel=1e-9, abs=1e-9), (
        f"{case_id}: {expression} -> {body['result_text']}"
    )
    assert actual.imag == pytest.approx(expected.imag, rel=1e-9, abs=1e-9), (
        f"{case_id}: {expression} -> {body['result_text']}"
    )


def test_edcx_b6_vc_fe_13_log_exp_uses_principal_branch():
    """Log(exp(3*pi*i)) is i*pi on the principal branch, not 3*i*pi."""
    response = client.post(
        "/api/v1/evaluate",
        json={"expression": "Log(exp(3*pi*i))"},
    )
    assert response.status_code == 200, response.text

    body = response.json()
    assert body["success"] is True, body
    assert body.get("error_code") is None, body
    assert isinstance(body.get("result_text"), str) and body["result_text"], body
    assert isinstance(body.get("result_latex"), str) and body["result_latex"], body
    assert body.get("result_approx") is None, body

    actual = _decode_complex_result(body["result_text"])
    assert actual.real == pytest.approx(0.0, abs=1e-9), body
    assert actual.imag == pytest.approx(math.pi, rel=1e-9, abs=1e-9), body
    assert actual.imag != pytest.approx(3 * math.pi, rel=1e-9, abs=1e-9), body


def test_edcx_b6_vc_fe_14_log_zero_returns_controlled_domain_error():
    """Log(0) is undefined and must not be reported as a successful value."""
    response = client.post("/api/v1/evaluate", json={"expression": "Log(0)"})
    assert response.status_code == 200, response.text

    body = response.json()
    assert body["success"] is False, body
    assert body.get("error_code") == "DOMAIN_ERROR", body
    assert body.get("result_text") in (None, ""), body


POWER_CASES = [
    ("VC-FE-16", "(-1)^i", cmath.exp(1j * cmath.log(-1))),
    ("VC-FE-17", "2^i", cmath.exp(1j * math.log(2))),
    ("VC-FE-18", "(1+i)^i", cmath.exp(1j * cmath.log(1 + 1j))),
]


@pytest.mark.parametrize(
    ("case_id", "expression", "expected"),
    POWER_CASES,
    ids=[case[0] for case in POWER_CASES],
)
def test_edcx_b6_complex_powers_match_independent_principal_oracle(
    case_id, expression, expected
):
    """Principal complex powers are checked against Python cmath, not SymPy."""
    response = client.post("/api/v1/evaluate", json={"expression": expression})
    assert response.status_code == 200, f"{case_id}: {response.text}"

    body = response.json()
    assert body["success"] is True, f"{case_id}: {body}"
    assert body.get("error_code") is None, f"{case_id}: {body}"
    assert isinstance(body.get("result_text"), str) and body["result_text"], (
        f"{case_id}: missing scalar result_text: {body}"
    )
    assert isinstance(body.get("result_latex"), str) and body["result_latex"], (
        f"{case_id}: missing result_latex: {body}"
    )
    assert body.get("result_approx") is None, f"{case_id}: {body}"

    actual = _decode_complex_result(body["result_text"])
    assert actual.real == pytest.approx(expected.real, rel=1e-9, abs=1e-9), (
        f"{case_id}: {expression} -> {body['result_text']}"
    )
    assert actual.imag == pytest.approx(expected.imag, rel=1e-9, abs=1e-9), (
        f"{case_id}: {expression} -> {body['result_text']}"
    )
