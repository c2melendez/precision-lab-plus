"""EDCX-B6 VC-FE-23..31 principal complex trigonometric scalars (test-first).

Independent oracle: Python cmath / math. Does not certify symbolic identities
or the remaining EDCX-B6 matrix rows.
"""
import cmath
import math

import pytest
import sympy
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# Expected values computed independently with cmath/math (principal branch).
TRIG_CASES = [
    ("VC-FE-23", "sin(i)", cmath.sin(1j)),
    ("VC-FE-24", "cos(i)", cmath.cos(1j)),
    ("VC-FE-25", "tan(i)", cmath.tan(1j)),
    ("VC-FE-26", "cot(i)", 1 / cmath.tan(1j)),
    ("VC-FE-27", "sin(1+i)", cmath.sin(1 + 1j)),
    ("VC-FE-28", "cos(1+i)", cmath.cos(1 + 1j)),
    ("VC-FE-29", "sin(pi/2+i)", cmath.sin(math.pi / 2 + 1j)),
    ("VC-FE-30", "cos(pi+i)", cmath.cos(math.pi + 1j)),
    ("VC-FE-31", "sin(2*i)", cmath.sin(2j)),
]


def _decode_complex_result(result_text: str) -> complex:
    """Decode only the calculator's emitted SymPy-style scalar text."""
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
    TRIG_CASES,
    ids=[case[0] for case in TRIG_CASES],
)
def test_edcx_b6_complex_trig_match_independent_principal_oracle(
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

    # result_approx is real-only; allow it only when imaginary part is ~0.
    if abs(expected.imag) <= 1e-9:
        assert body.get("result_approx") == pytest.approx(
            expected.real, rel=1e-9, abs=1e-9
        ), f"{case_id}: {body}"
    else:
        assert body.get("result_approx") is None, f"{case_id}: {body}"

    actual = _decode_complex_result(body["result_text"])
    assert actual.real == pytest.approx(expected.real, rel=1e-9, abs=1e-9), (
        f"{case_id}: {expression} -> {body['result_text']}"
    )
    assert actual.imag == pytest.approx(expected.imag, rel=1e-9, abs=1e-9), (
        f"{case_id}: {expression} -> {body['result_text']}"
    )
