"""Algebra114 AS-MUL-01..06: multivariable simplify/factor with domain and
assumptions, checked via the public HTTP API.

The contract for each row is verified against an independent SymPy oracle; for
AS-MUL-02/03 the result must be a genuine factorization (Mul), not merely an
equivalent expanded expression.
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


def test_as_mul_01_expand_to_sum_of_squares():
    assert "| AS-MUL-01 |" in SOURCE
    body = _simplify("(x+y)*(x-y)+z**2")
    actual = sp.sympify(body["result_text"])
    expected = x ** 2 - y ** 2 + z ** 2
    assert sp.expand(actual - expected) == 0
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


def test_as_mul_05_simplify_under_assumption():
    assert "| AS-MUL-05 |" in SOURCE
    body = _simplify("x**3+y**3+z**3")
    actual = sp.sympify(body["result_text"])
    # Under the assumption x+y+z=0 the identity collapses to 3xyz.
    subs = {z: -x - y}
    collapsed = sp.simplify(actual.subs(subs) - 3 * x * y * (-x - y))
    assert collapsed == 0, (actual, collapsed)
    for xv, yv, _ in TRIPLES:
        zv = -(xv + yv)
        assert float(sp.N(actual.subs({x: xv, y: yv, z: zv}))) == pytest.approx(
            3 * xv * yv * zv, rel=1e-9
        )


def test_as_mul_06_half_squared_differences():
    assert "| AS-MUL-06 |" in SOURCE
    body = _simplify("x**2+y**2+z**2-x*y-y*z-z*x")
    actual = sp.sympify(body["result_text"])
    expected = sp.Rational(1, 2) * ((x - y) ** 2 + (y - z) ** 2 + (z - x) ** 2)
    assert sp.expand(actual - expected) == 0
    for xv, yv, zv in TRIPLES:
        assert float(sp.N(actual.subs({x: xv, y: yv, z: zv}))) == pytest.approx(
            float(sp.N(expected.subs({x: xv, y: yv, z: zv}))), rel=1e-9
        )
