"""EDCX-B6 principal inverse complex trig/hyperbolic scalars (test-first).

Covered: VC-FE-43, 44, 46, 48 (domain error), 50, 51, 52.
Excluded for now (branch convention undecided): 45, 49, 53.
Independent oracle: cmath / math. Accepts exact symbolic real with
result_approx=None. Product function names: asin/acos/atan/asinh/acosh/atanh
(also arcsin/arccos/arctan aliases).
"""
import cmath
import math

import pytest
import sympy
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

INVERSE_CASES = [
    # VC-FE-43: arcsin(i) -> i*ln(1+sqrt(2))
    ("VC-FE-43", "asin(i)", cmath.asin(1j)),
    # VC-FE-44: arccos(i) -> pi/2 - i*ln(1+sqrt(2))
    ("VC-FE-44", "acos(i)", cmath.acos(1j)),
    # VC-FE-46: arctan(1+i)
    ("VC-FE-46", "atan(1+i)", cmath.atan(1 + 1j)),
    # VC-FE-50: arsinh(i) -> i*pi/2  (product name: asinh)
    ("VC-FE-50", "asinh(i)", cmath.asinh(1j)),
    # VC-FE-51: arcosh(0) -> i*pi/2
    ("VC-FE-51", "acosh(0)", cmath.acosh(0)),
    # VC-FE-52: arcosh(-1) -> i*pi
    ("VC-FE-52", "acosh(-1)", cmath.acosh(-1)),
]


def _decode_complex_result(result_text: str) -> complex:
    expr = sympy.sympify(
        result_text.replace("^", "**"),
        locals={"I": sympy.I, "E": sympy.E, "ln": sympy.log, "pi": sympy.pi},
    )
    value = complex(sympy.N(expr, 30))
    assert math.isfinite(value.real)
    assert math.isfinite(value.imag)
    return value


@pytest.mark.parametrize(
    ("case_id", "expression", "expected"),
    INVERSE_CASES,
    ids=[case[0] for case in INVERSE_CASES],
)
def test_edcx_b6_inverse_complex_match_independent_principal_oracle(
    case_id, expression, expected
):
    response = client.post("/api/v1/evaluate", json={"expression": expression})
    assert response.status_code == 200, f"{case_id}: {response.text}"

    body = response.json()
    assert body["success"] is True, f"{case_id}: {body}"
    assert body.get("error_code") is None, f"{case_id}: {body}"
    assert isinstance(body.get("result_text"), str) and body["result_text"], (
        f"{case_id}: missing result_text: {body}"
    )
    assert isinstance(body.get("result_latex"), str) and body["result_latex"], (
        f"{case_id}: missing result_latex: {body}"
    )

    approx = body.get("result_approx")
    if abs(expected.imag) <= 1e-9:
        if approx is not None:
            assert approx == pytest.approx(
                expected.real, rel=1e-9, abs=1e-9
            ), f"{case_id}: {body}"
    else:
        assert approx is None, f"{case_id}: {body}"

    actual = _decode_complex_result(body["result_text"])
    assert actual.real == pytest.approx(expected.real, rel=1e-9, abs=1e-9), (
        f"{case_id}: {expression} -> {body['result_text']}"
    )
    assert actual.imag == pytest.approx(expected.imag, rel=1e-9, abs=1e-9), (
        f"{case_id}: {expression} -> {body['result_text']}"
    )


def test_edcx_b6_vc_fe_48_atan_i_returns_controlled_domain_error():
    """arctan(i) is a singularity; must not succeed with a finite value."""
    response = client.post("/api/v1/evaluate", json={"expression": "atan(i)"})
    assert response.status_code == 200, response.text

    body = response.json()
    assert body["success"] is False, body
    assert body.get("error_code") == "DOMAIN_ERROR", body
    assert body.get("result_text") in (None, ""), body
