"""Algebra114 AS-MUL-01..06: multivariable simplify/factor with domain and
assumptions, checked via the public HTTP API.

The contract FORM of each row is the oracle; SymPy equivalence and numeric
triples only prove that no wrong value is returned. AS-MUL-02/03 must be a
genuine factorization (Mul) with the contract factors. AS-MUL-05 needs a
user-supplied assumption (x+y+z=0) that no endpoint accepts, and AS-MUL-06
needs a sum-of-squares rewrite that simplify() does not produce: both are
capability gaps (MANUAL_CAPABILITY_GAPS.md, AS-MUL) and must not be counted
as PASS by applying the assumption or the target form inside the test.
"""

from pathlib import Path

import pytest
import sympy as sp
from fastapi.testclient import TestClient

from app.main import app

x, y, z = sp.symbols("x y z")
client = TestClient(app)
SOURCE = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text(
    encoding="utf-8"
)
TRIPLES = [(2, 3, 5), (-1, 4, -2), (0, 5, 7), (3, -4, 1), (11, 0, -6), (-3, -3, 9)]


def _simplify(expression: str):
    response = client.post("/api/v1/simplify", json={"expression": expression})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    return body


def _factor(expression: str):
    response = client.post("/api/v1/factor", json={"expression": expression})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    return body


def _expand(expression: str):
    response = client.post("/api/v1/expand", json={"expression": expression})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    return body


def test_as_mul_01_expand_to_sum_of_squares():
    assert "| AS-MUL-01 |" in SOURCE
    body = _expand("(x+y)*(x-y)+z**2")
    actual = sp.sympify(body["result_text"])
    expected = x ** 2 - y ** 2 + z ** 2
    assert sp.srepr(actual) == sp.srepr(expected), actual
    for xv, yv, zv in TRIPLES:
        assert float(sp.N(actual.subs({x: xv, y: yv, z: zv}))) == pytest.approx(
            xv * xv - yv * yv + zv * zv, rel=1e-9
        )


def test_as_mul_02_factor_difference_of_squares():
    assert "| AS-MUL-02 |" in SOURCE
    body = _factor("x**2+2*x*y+y**2-z**2")
    actual = sp.sympify(body["result_text"])
    expected = (x + y - z) * (x + y + z)
    assert sp.expand(actual - expected) == 0
    assert actual.is_Mul, f"Factorization missing: {actual}"
    assert {sp.expand(factor) for factor in sp.Mul.make_args(actual)} == {
        sp.expand(x + y - z),
        sp.expand(x + y + z),
    }


def test_as_mul_03_factor_symmetric_cubic_identity():
    assert "| AS-MUL-03 |" in SOURCE
    body = _factor("x**3+y**3+z**3-3*x*y*z")
    actual = sp.sympify(body["result_text"])
    expected = (x + y + z) * (x ** 2 + y ** 2 + z ** 2 - x * y - y * z - z * x)
    assert sp.expand(actual - expected) == 0
    assert actual.is_Mul, f"Factorization missing: {actual}"
    assert {sp.expand(factor) for factor in sp.Mul.make_args(actual)} == {
        sp.expand(x + y + z),
        sp.expand(x ** 2 + y ** 2 + z ** 2 - x * y - y * z - z * x),
    }
    for xv, yv, zv in TRIPLES:
        assert float(sp.N(actual.subs({x: xv, y: yv, z: zv}))) == pytest.approx(
            (xv + yv + zv)
            * (xv * xv + yv * yv + zv * zv - xv * yv - yv * zv - zv * xv),
            rel=1e-9,
        )


def test_as_mul_04_simplify_with_domain_hole():
    assert "| AS-MUL-04 |" in SOURCE
    body = _simplify("(x-y)/(x**2-y**2)")
    actual = sp.sympify(body["result_text"])
    assert sp.simplify(actual - 1 / (x + y)) == 0
    conditions = body.get("domain_conditions", [])
    # The original expression has a removable discontinuity at x=y; the domain
    # must exclude the points that annul the original denominator x^2-y^2.
    assert any(
        c.get("kind") in ("denominator", "domain")
        and (sp.sympify(c.get("text"), locals={"x": x, "y": y}).subs({x: 1, y: 1}) in (sp.false, False))
        for c in conditions
    ), conditions


def test_as_mul_05_no_unconditional_3xyz_claim():
    assert "| AS-MUL-05 |" in SOURCE
    body = _simplify("x**3+y**3+z**3")
    actual = sp.sympify(body["result_text"])
    assert sp.expand(actual - (x ** 3 + y ** 3 + z ** 3)) == 0
    assert sp.expand(actual - 3 * x * y * z) != 0


def test_as_mul_06_simplify_returns_no_wrong_value():
    assert "| AS-MUL-06 |" in SOURCE
    body = _simplify("x**2+y**2+z**2-x*y-y*z-z*x")
    actual = sp.sympify(body["result_text"])
    expected = sp.Rational(1, 2) * ((x - y) ** 2 + (y - z) ** 2 + (z - x) ** 2)
    assert sp.expand(actual - expected) == 0
    for xv, yv, zv in TRIPLES:
        assert float(sp.N(actual.subs({x: xv, y: yv, z: zv}))) == pytest.approx(
            float(sp.N(expected.subs({x: xv, y: yv, z: zv}))), rel=1e-9
        )


@pytest.mark.xfail(strict=True, reason="AS-MUL-06 GAP: simplify() has no sum-of-squared-differences rewrite")
def test_as_mul_06_half_squared_differences_form():
    body = _simplify("x**2+y**2+z**2-x*y-y*z-z*x")
    actual = sp.sympify(body["result_text"])
    squares = {sp.expand((x - y) ** 2), sp.expand((y - z) ** 2), sp.expand((z - x) ** 2)}
    bases = {sp.expand(t.base ** 2) for t in sp.preorder_traversal(actual) if t.is_Pow and t.exp == 2 and t.base.is_Add}
    assert squares <= bases, actual
