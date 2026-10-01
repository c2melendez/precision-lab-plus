"""Bounded trig inequalities must include every satisfying interval."""
import os
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services import parsing, phase2_service

client = TestClient(app)


def _solve(expression, **extra):
    body = client.post("/api/v1/inequality", json={
        "inequality": expression, "variable": "x",
        "domain_lower": "0", "domain_upper": "2*pi",
        "domain_lower_inclusive": True, "domain_upper_inclusive": False,
        **extra,
    }).json()
    assert body["success"] is True, body
    # The process boundary keeps service execution out of the parent
    # coverage process. Verify the service directly as well as the API,
    # against the same independent expected sets below.
    result = phase2_service.compute_inequality(
        parsing.parse_inequality_tree(expression), "x",
        extra.get("domain_lower", "0"), extra.get("domain_upper", "2*pi"),
        extra.get("domain_lower_inclusive", True), extra.get("domain_upper_inclusive", False),
    )
    assert result.solution_set == sp.sympify(body["result_text"])
    return result.solution_set


def test_quadratic_in_sine_returns_all_three_components():
    actual = _solve("2*sin(x)^2-sin(x)-1<0")
    expected = sp.Union(
        sp.Interval.Ropen(0, sp.pi/2),
        sp.Interval.open(sp.pi/2, 7*sp.pi/6),
        sp.Interval.open(11*sp.pi/6, 2*sp.pi),
    )
    assert actual == expected


def test_product_of_sine_and_cosine_keeps_second_period():
    assert _solve("sin(x)*cos(x)>0") == sp.Union(
        sp.Interval.open(0, sp.pi/2), sp.Interval.open(sp.pi, 3*sp.pi/2)
    )


def test_absolute_sine_includes_four_equality_endpoints():
    assert _solve("abs(sin(x))>=sqrt(2)/2") == sp.Union(
        sp.Interval(sp.pi/4, 3*sp.pi/4), sp.Interval(5*sp.pi/4, 7*sp.pi/4)
    )


def test_multiple_periods_and_open_domain_endpoints():
    assert _solve("sin(x)>=0", domain_lower="-2*pi", domain_upper="2*pi",
                  domain_lower_inclusive=False) == sp.Union(
        sp.Interval.Lopen(-2*sp.pi, -sp.pi),
        sp.Interval(0, sp.pi), sp.FiniteSet(2*sp.pi)
    ).intersect(sp.Interval.open(-2*sp.pi, 2*sp.pi))
