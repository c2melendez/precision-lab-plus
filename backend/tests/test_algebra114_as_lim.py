"""Algebra114 AS-LIM-01..06 (sección M): robustez exacta y casos límite.

Contrato (qa/certification/algebra114_source.md, sección M).
Oráculo = valor contractual + dominio cuando aplica.
"""

from pathlib import Path

import pytest
import sympy as sp
from fastapi.testclient import TestClient

from app.main import app

x = sp.Symbol("x")
client = TestClient(app)
SOURCE = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text(
    encoding="utf-8"
)


def _simplify(expression: str) -> dict:
    response = client.post("/api/v1/simplify", json={"expression": expression})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    return body


def _factor(expression: str) -> dict:
    response = client.post("/api/v1/factor", json={"expression": expression})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    return body


def _value(body: dict) -> sp.Expr:
    return sp.sympify(body["result_text"])


def test_as_lim_fixture_rows_present():
    for case in range(1, 7):
        assert f"| AS-LIM-0{case} |" in SOURCE


def test_as_lim_01_cancels_to_one_plus_x_with_domain():
    body = _simplify("(1-x**2)/(1-x)")
    assert sp.simplify(_value(body) - (1 + x)) == 0, body
    domains = [c for c in body.get("domain_conditions", []) if c.get("kind") == "domain"]
    assert domains, body.get("domain_conditions")
    text = " ".join(c["text"] for c in domains)
    assert "x" in text and ("1" in text), text


def test_as_lim_02_geometric_sum_n5():
    body = _simplify("(x**5-1)/(x-1)")
    expected = x**4 + x**3 + x**2 + x + 1
    assert sp.simplify(_value(body) - expected) == 0, body


def test_as_lim_03_difference_of_powers_n3():
    body = _simplify("(x**3-8)/(x-2)")
    expected = x**2 + 2 * x + 4
    assert sp.simplify(_value(body) - expected) == 0, body


def test_as_lim_04_exact_product_of_sqrts():
    body = _simplify("sqrt(2)*sqrt(8)")
    assert _value(body) == 4, body
    assert body["result_text"].strip() in ("4", "4.0") or sp.sympify(body["result_text"]) == 4


def test_as_lim_05_factor_x6_minus_1():
    """Full real factorization of x^6-1 via the factor endpoint (AS-FAC channel)."""
    body = _factor("x**6-1")
    value = _value(body)
    assert sp.expand(value) == x**6 - 1, body
    # Contract factors over R: (x-1)(x+1)(x^2-x+1)(x^2+x+1)
    expected = (x - 1) * (x + 1) * (x**2 - x + 1) * (x**2 + x + 1)
    assert sp.simplify(value - expected) == 0, body
    # Must not leave a spurious (x^2+1) factor
    assert not any(
        sp.simplify(f - (x**2 + 1)) == 0 for f, _ in sp.factor_list(value)[1]
    ), body


def test_as_lim_06_x100_stays_compact():
    body = _simplify("(x**100-1)/(x-1)")
    text = body.get("result_text") or ""
    latex = body.get("result_latex") or ""
    combined = text + latex
    power_hits = combined.count("x**") + combined.count("x^")
    assert power_hits < 20, (power_hits, combined[:300])
    val = _value(body)
    assert val.subs(x, 2) == sum(2**k for k in range(100))
