"""Trigonometry EV-I-01..06, EV-I-08 and EV-I-11 over HTTP evaluate (ASCII channel).

Each case verifies the frozen matrix row and the documented exact value.
"""
from pathlib import Path
import gzip
import re

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app

SOURCE_GZ = (
    Path(__file__).resolve().parents[2]
    / "qa/certification/legacy_sources/ejercicios_trigonometria.md.gz"
)


def _matrix_row(case_id: str) -> str:
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    return next((line for line in text.splitlines() if f"| {case_id} |" in line), "")


def _evaluate(client: TestClient, expression: str) -> dict:
    response = client.post("/api/v1/evaluate", json={"expression": expression})
    assert response.status_code == 200, response.text
    return response.json()


def _value(payload: dict) -> sp.Expr:
    assert payload["success"] is True, payload
    return sp.sympify(payload["result_text"].replace("^", "**"))


CASES = [
    ("EV-I-01", "asin(1/2)", r"\arcsin\left(\frac{1}{2}\right)", sp.pi / 6),
    ("EV-I-02", "acos(-1/2)", r"\arccos\left(-\frac{1}{2}\right)", 2 * sp.pi / 3),
    ("EV-I-03", "atan(1)", r"\arctan(1)", sp.pi / 4),
    ("EV-I-04", "atan(sqrt(3))", r"\arctan\left(\sqrt{3}\right)", sp.pi / 3),
    ("EV-I-05", "acsc(2)", r"\operatorname{arccsc}(2)", sp.pi / 6),
    ("EV-I-06", "asec(2)", r"\operatorname{arcsec}(2)", sp.pi / 3),
]


def test_ev_i_source_rows_present():
    for case_id, _expr, latex, _expected in CASES:
        row = _matrix_row(case_id)
        assert row, f"{case_id} row missing"
        assert latex in row, (case_id, row)
    assert "\\operatorname{arccot}(0)" in _matrix_row("EV-I-08")
    assert "\\cos(\\arctan 2)" in _matrix_row("EV-I-11")


def test_ev_i_01_to_06_values():
    with TestClient(app) as client:
        for case_id, expression, _latex, expected in CASES:
            payload = _evaluate(client, expression)
            assert sp.simplify(_value(payload) - expected) == 0, (case_id, payload)


def test_ev_i_08_acot_zero_and_ev_i_11_cos_atan_two():
    with TestClient(app) as client:
        acot_zero = _evaluate(client, "acot(0)")
        cos_atan = _evaluate(client, "cos(atan(2))")
    assert sp.simplify(_value(acot_zero) - sp.pi / 2) == 0, acot_zero
    got = _value(cos_atan)
    assert sp.simplify(got - sp.sqrt(5) / 5) == 0, cos_atan
