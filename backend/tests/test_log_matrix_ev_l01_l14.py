"""Trigonometry-adjacent matrix EV-L-01..14: logarithms over HTTP evaluate.

Plus accepts `log(x, b)` for base-b logarithms and simplifies ratios exactly
(log(8,4) = 3/2). EV-L-09 (product of two base-b logs) is not covered: the
parser does not accept the `\\log_{2}(3)\\cdot...` spelling yet, tracked as an
open item in both engines.
"""
from pathlib import Path
import gzip

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app

SOURCE_GZ = (
    Path(__file__).resolve().parents[2]
    / "qa/certification/legacy_sources/matriz_log_exp_radicales.md.gz"
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


def test_ev_l_source_rows_present():
    for i in range(1, 15):
        assert _row(f"EV-L-{i:02d}"), f"EV-L-{i:02d} row missing"


def test_ev_l_exact_values():
    cases = [
        ("ln(E**3)", 3),
        ("log(8,2)", 3),
        ("log(0.001,10)", -3),
        ("log(1/27,3)", -3),
        ("log(8,4)", sp.Rational(3, 2)),
        ("log(2,8)", sp.Rational(1, 3)),
        ("ln(sqrt(E))", sp.Rational(1, 2)),
    ]
    with TestClient(app) as client:
        for expression, expected in cases:
            payload = _evaluate(client, expression)
            assert sp.simplify(_value(payload) - expected) == 0, (expression, payload)


def test_ev_l_approximations():
    with TestClient(app) as client:
        ln2 = _evaluate(client, "ln(2)")
        log23 = _evaluate(client, "log(3,2)")
        big = _evaluate(client, "ln(10^50)")
    assert abs(ln2["result_approx"] - 0.693147181) <= 5e-10, ln2
    assert abs(log23["result_approx"] - 1.584962501) <= 5e-10, log23
    assert abs(big["result_approx"] - 115.12925465) <= 5e-8, big
    assert sp.simplify(_value(big) - 50 * sp.log(10)) == 0, big


def test_ev_l_product_of_base_logs():
    with TestClient(app) as client:
        ascii_payload = _evaluate(client, "log(3,2)*log(4,3)")
        latex_payload = _evaluate(client, r"\log_{2}(3)\cdot\log_{3}(4)")
    assert sp.simplify(_value(ascii_payload) - 2) == 0, ascii_payload
    assert sp.simplify(_value(latex_payload) - 2) == 0, latex_payload


def test_ev_l_undefined_complex_and_invalid_base():
    with TestClient(app) as client:
        zero = _evaluate(client, "ln(0)")
        negative = _evaluate(client, "ln(-1)")
        bad_bases = [
            _evaluate(client, "log(5,1)"),
            _evaluate(client, "log(5,0)"),
            _evaluate(client, "log(5,-2)"),
        ]
    assert zero["success"] is False and zero["error_code"] == "DOMAIN_ERROR", zero
    assert negative["success"] is True, negative
    assert sp.simplify(_value(negative) - sp.I * sp.pi) == 0, negative
    for bad_base in bad_bases:
        assert bad_base["success"] is False, bad_base
        assert bad_base["error_code"] == "DOMAIN_ERROR", bad_base
        diagnostic = str(bad_base).lower()
        assert "base" in diagnostic or "logaritmo" in diagnostic, bad_base
