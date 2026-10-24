"""Algebra114 AS-DOM-01..06: results keep the ORIGINAL real domain.

Each case checks the simplified/solved result, the combined real-domain condition
(kind="domain", SymPy-parsable) against an independent sample oracle, and HTTP.
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
SAMPLES = [-3, -1, sp.Rational(-1, 2), 0, sp.Rational(1, 2), 1, sp.Rational(3, 2), 2, 5]

DOMAIN_CASES = [
    ("AS-DOM-01", "(x**2-1)/(x-1)", "x+1", lambda t: t != 1),
    ("AS-DOM-02", "(x-1)/(x**2-1)", "1/(x+1)", lambda t: t not in (1, -1)),
    ("AS-DOM-04", "sqrt(x**2)/x", "Abs(x)/x", lambda t: t != 0),
    ("AS-DOM-05", "1/sqrt(x-1)", None, lambda t: t > 1),
    ("AS-DOM-06", "sqrt(x/(x-1))", None, lambda t: t <= 0 or t > 1),
]


def _simplify(expression):
    response = client.post("/api/v1/simplify", json={"expression": expression})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    return body


@pytest.mark.parametrize("case_id,expression,expected,in_domain", DOMAIN_CASES)
def test_as_dom_simplify_keeps_original_real_domain(case_id, expression, expected, in_domain):
    assert f"| {case_id} | " in SOURCE
    body = _simplify(expression)
    if expected is not None:
        assert sp.simplify(sp.sympify(body["result_text"]) - sp.sympify(expected)) == 0, body
    summaries = [c for c in body["domain_conditions"] if c["kind"] == "domain"]
    assert len(summaries) == 1, (case_id, body["domain_conditions"])
    relation = sp.sympify(summaries[0]["text"], locals={"x": x})
    for t in SAMPLES:
        assert bool(relation.subs(x, t)) is bool(in_domain(t)), (case_id, t, summaries[0]["text"])
    assert summaries[0]["latex"]


def test_as_dom_04_sign_cases():
    body = _simplify("sqrt(x**2)/x")
    assert sp.sympify(body["result_text"]) == sp.Abs(x) / x
    text = " ".join(step["description"] for step in body["steps"])
    assert "vale 1 si x > 0 y -1 si x < 0" in text, text
    for t in (-2, sp.Rational(-1, 3), sp.Rational(1, 3), 4):
        assert (sp.Abs(x) / x).subs(x, t) == (1 if t > 0 else -1)


def test_as_dom_03_solve_discards_point_outside_domain():
    assert "| AS-DOM-03 | " in SOURCE
    response = client.post(
        "/api/v1/solve", json={"equation": "(x**2-1)/(x-1)=0", "variable": "x", "angle_unit": "rad"}
    )
    body = response.json()
    assert response.status_code == 200 and body["success"] is True, body
    assert body["result_type"] == "equation_solutions"
    assert [sp.sympify(s["text"]) for s in body["result_data"]] == [-1]
    text = " ".join(step["description"] for step in body["steps"])
    assert "x≠1" in text and "x = 1 anula el numerador pero no pertenece al dominio" in text, text
