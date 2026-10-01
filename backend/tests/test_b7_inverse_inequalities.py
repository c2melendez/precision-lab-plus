"""Real inverse-function comparisons retain domain and endpoint semantics."""
import os

os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")

import pytest
import sympy as sp

from app.services import parsing, phase2_service


@pytest.mark.parametrize("expression,expected", [
    ("asin(x)<acos(x)", sp.Interval.Ropen(-1, sp.sqrt(2)/2)),
    ("asin(x)<=acos(x)", sp.Interval(-1, sp.sqrt(2)/2)),
    ("asin(x)>acos(x)", sp.Interval.Lopen(sp.sqrt(2)/2, 1)),
    ("asin(x)>=acos(x)", sp.Interval(sp.sqrt(2)/2, 1)),
    ("acos(x)<asin(x)", sp.Interval.Lopen(sp.sqrt(2)/2, 1)),
    ("acos(x)>=asin(x)", sp.Interval(-1, sp.sqrt(2)/2)),
    ("asin(2*x)<acos(2*x)", sp.Interval.Ropen(-sp.Rational(1,2), sp.sqrt(2)/4)),
    ("asin(-x)<acos(-x)", sp.Interval.Lopen(-sp.sqrt(2)/2, 1)),
])
def test_principal_inverse_comparison_service(expression, expected):
    actual = phase2_service.compute_inequality(parsing.parse_inequality_tree(expression), "x")
    assert actual.solution_set == expected
    assert actual.solution_set.contains(-2) is sp.false
    assert actual.solution_set.contains(2) is sp.false


@pytest.mark.parametrize("expression,expected", [("1<2", sp.S.Reals), ("2<1", sp.EmptySet)])
def test_constant_comparison_service(expression, expected):
    actual = phase2_service.compute_inequality(parsing.parse_inequality_tree(expression), "x")
    assert actual.solution_set == expected


def test_inverse_comparison_clips_to_requested_open_domain_service():
    actual = phase2_service.compute_inequality(
        parsing.parse_inequality_tree("asin(x)<acos(x)"), "x", "-1", "0", False, False,
    )
    assert actual.solution_set == sp.Interval.open(-1, 0)


def test_inverse_comparison_with_disjoint_requested_domain_service():
    actual = phase2_service.compute_inequality(
        parsing.parse_inequality_tree("asin(x)<acos(x)"), "x", "1", "2",
    )
    assert actual.solution_set == sp.EmptySet


def test_inverse_comparison_api_returns_exact_interval():
    from fastapi.testclient import TestClient
    from app.main import app

    body = TestClient(app).post("/api/v1/inequality", json={
        "inequality": "asin(x)<acos(x)", "variable": "x",
        "domain_lower": "-1", "domain_upper": "1",
    }).json()
    assert body["success"] is True, body
    assert sp.sympify(body["result_text"]) == sp.Interval.Ropen(-1, sp.sqrt(2)/2)
