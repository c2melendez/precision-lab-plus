"""Trigonometry EV-I-09 / EV-I-10: principal range and Pythagorean composition.

EV-I-09 (`\\arcsin(\\sin 2)` = pi - 2) and EV-I-10 (`\\sin(\\arccos 3/5)` = 4/5)
were the two remaining open rows of the inverse-trig group on the Lite side.
Plus already resolved both correctly; these tests freeze that behaviour as a
permanent bilateral regression so a future change cannot silently reintroduce
the collapsed branch (arcsin(sin 2) = 2) or the unevaluated composition.
"""
from pathlib import Path
import gzip

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


def _value(payload: dict):
    assert payload["success"] is True, payload
    return sp.sympify(payload["result_text"].replace("^", "**"))


def test_ev_i09_source_row_documents_pi_minus_two():
    row = _row("EV-I-09")
    assert row, "EV-I-09 row missing"
    assert r"\arcsin(\sin 2)" in row
    assert r"\pi-2" in row
    assert "1.141592654" in row


def test_ev_i10_source_row_documents_four_fifths():
    row = _row("EV-I-10")
    assert row, "EV-I-10 row missing"
    assert r"\arccos\frac{3}{5}" in row
    assert r"\frac{4}{5}" in row


def test_ev_i09_asin_sin_two_is_pi_minus_two():
    with TestClient(app) as client:
        payload = _evaluate(client, "asin(sin(2))")
    assert _value(payload) != 2, payload
    assert sp.simplify(_value(payload) - (sp.pi - 2)) == 0, payload
    assert abs(payload["result_approx"] - 1.141592654) <= 5e-10, payload


def test_ev_i09_principal_branch_inside_domain_is_unchanged():
    with TestClient(app) as client:
        sixth = _evaluate(client, "asin(sin(pi/6))")
        cosine = _evaluate(client, "acos(cos(2))")
        tangent = _evaluate(client, "atan(tan(2))")
    assert sp.simplify(_value(sixth) - sp.pi / 6) == 0, sixth
    assert sp.simplify(_value(cosine) - 2) == 0, cosine
    assert sp.simplify(_value(tangent) - (2 - sp.pi)) == 0, tangent


def test_ev_i10_sin_acos_three_fifths_is_four_fifths():
    with TestClient(app) as client:
        payload = _evaluate(client, "sin(acos(3/5))")
        negative = _evaluate(client, "sin(acos(-3/5))")
        companion = _evaluate(client, "cos(asin(3/5))")
    assert sp.simplify(_value(payload) - sp.Rational(4, 5)) == 0, payload
    assert sp.simplify(_value(negative) - sp.Rational(4, 5)) == 0, negative
    assert sp.simplify(_value(companion) - sp.Rational(4, 5)) == 0, companion
    assert abs(payload["result_approx"] - 0.8) <= 5e-10, payload


def test_ev_i12_out_of_domain_still_reports_domain_error():
    with TestClient(app) as client:
        payload = _evaluate(client, "asin(2)")
    assert payload["success"] is False, payload
    assert payload["error_code"] == "DOMAIN_ERROR", payload
