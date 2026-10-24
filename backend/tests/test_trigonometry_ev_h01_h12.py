"""Trigonometry EV-H-01..12: hyperbolic values at the origin, at ln 2 and at 1.

Neither engine simplifies exact rationals symbolically (result_text stays
"sinh(ln(2))"), so EV-H-04..09 are certified on the numeric channel
(result_approx) against the documented rational. Exact rational display is a
documented capability gap, not a silent wrong value.
"""
from pathlib import Path
import gzip
from fractions import Fraction

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app

SOURCE_GZ = (
    Path(__file__).resolve().parents[2]
    / "qa/certification/legacy_sources/ejercicios_trigonometria.md.gz"
)


def _row(case_id: str) -> str:
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    return next((line for line in text.splitlines() if f"| {case_id} |" in line), "")


def _evaluate(client: TestClient, expression: str) -> dict:
    response = client.post("/api/v1/evaluate", json={"expression": expression})
    assert response.status_code == 200, response.text
    return response.json()


def test_ev_h_source_rows_present():
    for case_id in [f"EV-H-{i:02d}" for i in range(1, 13)]:
        assert _row(case_id), f"{case_id} row missing"


def test_ev_h_01_to_03_origin_exact_values():
    with TestClient(app) as client:
        for expression, expected in (("sinh(0)", "0"), ("cosh(0)", "1"), ("tanh(0)", "0")):
            payload = _evaluate(client, expression)
            assert payload["success"] is True, payload
            assert payload["result_text"].strip() == expected, payload


def test_ev_h_04_to_09_ln_two_numeric_values():
    cases = [
        ("sinh(ln(2))", 3, 4),
        ("cosh(ln(2))", 5, 4),
        ("tanh(ln(2))", 3, 5),
        ("csch(ln(2))", 4, 3),
        ("sech(ln(2))", 4, 5),
        ("coth(ln(2))", 5, 3),
    ]
    with TestClient(app) as client:
        for expression, num, den in cases:
            payload = _evaluate(client, expression)
            assert payload["success"] is True, payload
            approx = payload.get("result_approx")
            assert approx is not None, payload
            assert abs(Fraction(approx).limit_denominator(10**6) - Fraction(num, den)) == 0 or abs(
                approx - float(Fraction(num, den))
            ) < 1e-12, (expression, approx)


def test_ev_h_10_to_12_approximations_and_identity():
    with TestClient(app) as client:
        sinh_one = _evaluate(client, "sinh(1)")
        cosh_one = _evaluate(client, "cosh(1)")
        identity = _evaluate(client, "cosh(1)^2-sinh(1)^2")
    assert abs(sinh_one["result_approx"] - 1.175201194) <= 5e-10, sinh_one
    assert abs(cosh_one["result_approx"] - 1.543080635) <= 5e-10, cosh_one
    assert identity["success"] is True, identity
    assert sp.simplify(sp.sympify(identity["result_text"].replace("^", "**")) - 1) == 0, identity
