"""EDCX-B6 VC-FE-32..36: numerical substitution checks for symbolic identities.

These tests exercise the public /evaluate channel with explicit numeric
substitutions. They provide finite, scoped evidence only; they do not prove
the identities for all real/complex inputs or certify symbolic assumption
handling. Expected values are computed independently with Python math/cmath.
"""
import cmath
import math

import pytest
import sympy
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

REAL_PAIRS = [
    (0.4, 0.7),
    (-1.1, 0.3),
    (2.2, -0.8),
]

COMPLEX_POINTS = [
    ("0.4+0.7*i", 0.4 + 0.7j),
    ("-1.1+0.3*i", -1.1 + 0.3j),
    ("2.2-0.8*i", 2.2 - 0.8j),
]


def _decode_result(result_text: str) -> complex:
    """Decode the public scalar text without using it as the oracle."""
    expression = sympy.sympify(
        result_text.replace("^", "**"),
        locals={"I": sympy.I, "E": sympy.E, "pi": sympy.pi, "ln": sympy.log},
    )
    value = complex(sympy.N(expression, 30))
    assert math.isfinite(value.real)
    assert math.isfinite(value.imag)
    return value


@pytest.mark.parametrize(("x", "y"), REAL_PAIRS)
@pytest.mark.parametrize(
    ("case_id", "expression", "oracle"),
    [
        (
            "VC-FE-32",
            "abs(sin(x+i*y))^2",
            lambda x, y: math.sin(x) ** 2 + math.sinh(y) ** 2,
        ),
        (
            "VC-FE-33",
            "abs(cos(x+i*y))^2",
            lambda x, y: math.cos(x) ** 2 + math.sinh(y) ** 2,
        ),
    ],
)
def test_edcx_b6_symbolic_modulus_identities_at_real_substitutions(
    case_id, expression, oracle, x, y
):
    # Independent check that the source identity's complex left side and
    # real right side agree for this declared real pair.
    complex_input = complex(x, y)
    if case_id == "VC-FE-32":
        lhs = abs(cmath.sin(complex_input)) ** 2
    else:
        lhs = abs(cmath.cos(complex_input)) ** 2
    expected = oracle(x, y)
    assert lhs == pytest.approx(expected, rel=1e-12, abs=1e-12)

    response = client.post(
        "/api/v1/evaluate",
        json={"expression": expression, "substitutions": {"x": repr(x), "y": repr(y)}},
    )
    assert response.status_code == 200, f"{case_id}: {response.text}"
    body = response.json()
    assert body["success"] is True, f"{case_id}: {body}"
    assert body.get("error_code") is None, f"{case_id}: {body}"
    assert isinstance(body.get("result_text"), str) and body["result_text"], body
    assert isinstance(body.get("result_latex"), str) and body["result_latex"], body
    actual = _decode_result(body["result_text"])
    assert actual.real == pytest.approx(expected, rel=1e-9, abs=1e-9), body
    assert actual.imag == pytest.approx(0.0, abs=1e-9), body
    assert body.get("result_approx") == pytest.approx(expected, rel=1e-9, abs=1e-9), body


@pytest.mark.parametrize(("raw_z", "z"), COMPLEX_POINTS)
@pytest.mark.parametrize(
    ("case_id", "expression", "oracle"),
    [
        (
            "VC-FE-34",
            "(exp(i*z)+exp(-i*z))/2",
            cmath.cos,
        ),
        (
            "VC-FE-35",
            "(exp(i*z)-exp(-i*z))/(2*i)",
            cmath.sin,
        ),
    ],
)
def test_edcx_b6_exponential_trig_identities_at_complex_substitutions(
    case_id, expression, oracle, raw_z, z
):
    expected = oracle(z)
    response = client.post(
        "/api/v1/evaluate",
        json={"expression": expression, "substitutions": {"z": raw_z}},
    )
    assert response.status_code == 200, f"{case_id}: {response.text}"
    body = response.json()
    assert body["success"] is True, f"{case_id}: {body}"
    assert body.get("error_code") is None, f"{case_id}: {body}"
    assert isinstance(body.get("result_text"), str) and body["result_text"], body
    assert isinstance(body.get("result_latex"), str) and body["result_latex"], body
    assert body.get("result_approx") is None, body
    actual = _decode_result(body["result_text"])
    assert actual.real == pytest.approx(expected.real, rel=1e-9, abs=1e-9), body
    assert actual.imag == pytest.approx(expected.imag, rel=1e-9, abs=1e-9), body


@pytest.mark.parametrize(("raw_z", "z"), COMPLEX_POINTS)
def test_edcx_b6_pythagorean_identity_at_complex_substitutions(raw_z, z):
    response = client.post(
        "/api/v1/evaluate",
        json={
            "expression": "sin(z)^2+cos(z)^2",
            "substitutions": {"z": raw_z},
        },
    )
    assert response.status_code == 200, f"VC-FE-36: {response.text}"
    body = response.json()
    assert body["success"] is True, f"VC-FE-36: {body}"
    assert body.get("error_code") is None, f"VC-FE-36: {body}"
    assert isinstance(body.get("result_text"), str) and body["result_text"], body
    assert isinstance(body.get("result_latex"), str) and body["result_latex"], body
    actual = _decode_result(body["result_text"])
    assert actual.real == pytest.approx(1.0, rel=1e-9, abs=1e-9), body
    assert actual.imag == pytest.approx(0.0, abs=1e-9), body
    # result_approx is optional and only populated when the evaluator's
    # numeric approximation is classified as real. The exact scalar text
    # above is independently decoded and checked against the oracle.
    assert body.get("result_approx") is None or body.get("result_approx") == pytest.approx(1.0, abs=1e-9), body
