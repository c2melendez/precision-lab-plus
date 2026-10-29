"""EDCX-B6 VC-FE-42 and VC-FE-47 — inverse formulas evaluated at real points.

Independent oracle: math / cmath. These rows evaluate a complex formula at a
specific real substitution and expect a real principal value.
"""
import math

import pytest
import sympy
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# VC-FE-42: -i*ln(i*z + sqrt(1-z^2)) at z=1/2 -> pi/6
# VC-FE-47: (1/(2i))*ln((1+i*z)/(1-i*z)) at z=1 -> pi/4
FORMULA_CASES = [
    (
        "VC-FE-42",
        "-i*ln(i*(1/2)+sqrt(1-(1/2)^2))",
        math.pi / 6,
    ),
    (
        "VC-FE-47",
        "(1/(2*i))*ln((1+i*1)/(1-i*1))",
        math.pi / 4,
    ),
]


def _decode_scalar(result_text: str) -> complex:
    expr = sympy.sympify(
        result_text.replace("^", "**"),
        locals={"I": sympy.I, "E": sympy.E, "ln": sympy.log, "pi": sympy.pi},
    )
    value = complex(sympy.N(expr, 30))
    assert math.isfinite(value.real)
    assert math.isfinite(value.imag)
    return value


@pytest.mark.parametrize(
    ("case_id", "expression", "expected_real"),
    FORMULA_CASES,
    ids=[case[0] for case in FORMULA_CASES],
)
def test_edcx_b6_formula_real_points_match_independent_oracle(
    case_id, expression, expected_real
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

    # Expected value is real; product may return exact symbolic or numeric approx.
    approx = body.get("result_approx")
    if approx is not None:
        assert approx == pytest.approx(
            expected_real, rel=1e-9, abs=1e-9
        ), f"{case_id}: {body}"

    actual = _decode_scalar(body["result_text"])
    assert actual.real == pytest.approx(expected_real, rel=1e-9, abs=1e-9), (
        f"{case_id}: {expression} -> {body['result_text']}"
    )
    assert abs(actual.imag) <= 1e-9, (
        f"{case_id}: expected real, got imag={actual.imag} from {body['result_text']}"
    )
