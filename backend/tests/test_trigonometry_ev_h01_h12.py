"""Trigonometry EV-H-01..12: hyperbolic values at the origin, at ln 2 and at 1.

Neither engine simplifies exact rationals symbolically (result_text stays
"sinh(ln(2))"), so EV-H-04..09 are certified on the numeric channel
(result_approx) against the documented rational. Exact rational display is a
documented capability gap, not a silent wrong value.
"""
from pathlib import Path
import gzip
from fractions import Fraction

import pytest
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


@pytest.mark.parametrize("case_id,expression,expected", [
    ("EV-H-01", "sinh(0)", "0"),
    ("EV-H-02", "cosh(0)", "1"),
    ("EV-H-03", "tanh(0)", "0"),
])
def test_hyperbolic_origin(case_id, expression, expected):
    assert _row(case_id)
    with TestClient(app) as client:
        payload = _evaluate(client, expression)
    assert payload["success"] is True, payload
    assert payload["result_text"].strip() == expected, payload


@pytest.mark.parametrize("case_id,expression,num,den", [
    ("EV-H-04", "sinh(ln(2))", 3, 4),
    ("EV-H-05", "cosh(ln(2))", 5, 4),
    ("EV-H-06", "tanh(ln(2))", 3, 5),
    ("EV-H-07", "csch(ln(2))", 4, 3),
    ("EV-H-08", "sech(ln(2))", 4, 5),
    ("EV-H-09", "coth(ln(2))", 5, 3),
])
def test_hyperbolic_ln_two(case_id, expression, num, den):
    assert _row(case_id)
    with TestClient(app) as client:
        payload = _evaluate(client, expression)
    assert payload["success"] is True, payload
    approx = payload.get("result_approx")
    assert approx is not None, payload
    assert abs(Fraction(approx).limit_denominator(10**6) - Fraction(num, den)) == 0 or abs(
        approx - float(Fraction(num, den))
    ) < 1e-12, (expression, approx)


@pytest.mark.parametrize("case_id,expression,expected", [
    ("EV-H-10", "sinh(1)", 1.175201194),
    ("EV-H-11", "cosh(1)", 1.543080635),
])
def test_hyperbolic_approximation(case_id, expression, expected):
    assert _row(case_id)
    with TestClient(app) as client:
        payload = _evaluate(client, expression)
    assert payload["success"] is True, payload
    assert abs(payload["result_approx"] - expected) <= 5e-10, payload


def test_ev_h_12_identity():
    assert _row("EV-H-12")
    with TestClient(app) as client:
        identity = _evaluate(client, "cosh(1)^2-sinh(1)^2")
    assert identity["success"] is True, identity
    assert sp.simplify(sp.sympify(identity["result_text"].replace("^", "**")) - 1) == 0, identity
