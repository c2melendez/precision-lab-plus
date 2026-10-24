"""Trigonometry EV-I-07: arccot(-1) = 3*pi/4 with the principal range (0, pi).

SymPy's acot uses (-pi/2, pi/2] and returns -pi/4 at -1; the frozen matrix
requires the principal branch. The endpoint rewrites acot(x) as
pi/2 - atan(x) before evaluating, which is exact for every real x.
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


def test_ev_i07_source_row_documents_three_pi_over_four():
    row = _row("EV-I-07")
    assert row, "EV-I-07 row missing"
    assert r"\operatorname{arccot}(-1)" in row
    assert r"\frac{3\pi}{4}" in row


def test_ev_i07_arccot_negative_one_is_three_pi_over_four():
    with TestClient(app) as client:
        payload = _evaluate(client, "acot(-1)")
    assert payload["success"] is True, payload
    got = sp.sympify(payload["result_text"].replace("^", "**"))
    assert sp.simplify(got - 3 * sp.pi / 4) == 0, payload


def test_ev_i07_branch_is_consistent_at_zero_and_one():
    with TestClient(app) as client:
        zero = _evaluate(client, "acot(0)")
        one = _evaluate(client, "acot(1)")
    assert sp.simplify(sp.sympify(zero["result_text"]) - sp.pi / 2) == 0, zero
    assert sp.simplify(sp.sympify(one["result_text"]) - sp.pi / 4) == 0, one
