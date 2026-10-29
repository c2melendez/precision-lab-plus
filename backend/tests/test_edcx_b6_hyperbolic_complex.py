"""EDCX-B6 VC-FE-37..41 principal complex hyperbolic scalars (test-first).

Independent oracle: Python cmath / math. Accepts exact symbolic real results
with result_approx=None (same harness rule as VC-FE-29/30). Does not certify
the remaining EDCX-B6 matrix rows.
"""
import cmath
import math

import pytest
import sympy
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# Expected values from independent cmath/math (principal branch).
# VC-FE-37 is a paired row in the matrix; split into 37a/37b for harness.
HYPERBOLIC_CASES = [
    ("VC-FE-37a", "sinh(i*pi)", cmath.sinh(1j * math.pi)),
    ("VC-FE-37b", "cosh(i*pi)", cmath.cosh(1j * math.pi)),
    ("VC-FE-38", "sinh(i*pi/2)", cmath.sinh(1j * math.pi / 2)),
    ("VC-FE-39", "tanh(i*pi/4)", cmath.tanh(1j * math.pi / 4)),
    ("VC-FE-40", "cosh(1+i*pi)", cmath.cosh(1 + 1j * math.pi)),
    ("VC-FE-41", "sinh(1+i*pi/2)", cmath.sinh(1 + 1j * math.pi / 2)),
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
    HYPERBOLIC_CASES,
    ids=[case[0] for case in HYPERBOLIC_CASES],
)
def test_edcx_b6_complex_hyperbolic_match_independent_principal_oracle(
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

    # result_approx is real-only. Exact symbolic real forms (e.g. -cosh(1))
    # may leave it None; that is accepted when the decoded value matches.
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
