"""IN-D-05: two closed intervals in the frozen [0,2*pi) period."""
import gzip
from pathlib import Path
from unittest.mock import patch
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.parsing import parse_inequality_tree
from app.services.phase2_service import compute_inequality

EXPECTED = sp.Union(sp.Interval(sp.pi/4, 3*sp.pi/4), sp.Interval(5*sp.pi/4, 7*sp.pi/4))


def test_in_d05_source_row_is_frozen():
    source = gzip.decompress((Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/ejercicios_trigonometria.md.gz").read_bytes()).decode()
    row = next(line for line in source.splitlines() if "| IN-D-05 |" in line)
    assert [s.strip() for s in row.split("|") if s.strip()] == [
        "IN-D-05", r"`\lvert\sin x\rvert\ge\frac{\sqrt{2}}{2},\quad x\in[0,2\pi)`",
        r"`\left[\frac{\pi}{4},\frac{3\pi}{4}\right]\cup\left[\frac{5\pi}{4},\frac{7\pi}{4}\right]`",
    ]


def test_in_d05_service_returns_both_closed_components_and_all_four_endpoints():
    for expression, var in [("abs(sin(x))>=sqrt(2)/2", "x"),
                            ("sqrt(2)/2<=abs(sin(x))", "x"), ("abs(sin(t))>=sqrt(2)/2", "t")]:
        result = compute_inequality(parse_inequality_tree(expression), var)
        assert result.solution_set == EXPECTED, result.solution_set
        for boundary in [sp.pi/4, 3*sp.pi/4, 5*sp.pi/4, 7*sp.pi/4]:
            assert result.solution_set.contains(boundary) is sp.S.true
        for value in [0, sp.pi, 2*sp.pi]:
            assert result.solution_set.contains(value) is sp.S.false
        for value in [sp.pi/2, 3*sp.pi/2]:
            assert result.solution_set.contains(value) is sp.S.true
        assert result.warnings and "[0, 2*pi)" in result.warnings[0]


def test_in_d05_http_returns_exact_union():
    with TestClient(app) as client:
        response = client.post("/api/v1/inequality", json={"inequality": "abs(sin(x))>=sqrt(2)/2", "variable": "x"})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["operation"] == "inequality" and body["request_id"]
    assert body["result_text"] == str(EXPECTED)
    assert body["result_latex"] == sp.latex(EXPECTED)
    assert body["warnings"] and "[0, 2*pi)" in body["warnings"][0]


def test_in_d05_independent_exact_sign_and_squared_form_oracle():
    for angle, expected in [(0, False), (sp.pi/4, True), (sp.pi/2, True), (3*sp.pi/4, True),
                            (sp.pi, False), (5*sp.pi/4, True), (3*sp.pi/2, True), (7*sp.pi/4, True), (2*sp.pi, False)]:
        value = sp.Abs(sp.sin(angle))
        assert bool(value >= sp.sqrt(2)/2) is expected
        assert bool(sp.sin(angle)**2 >= sp.Rational(1, 2)) is expected


def test_in_d05_non_matching_comparisons_reach_the_original_solver():
    # Sentinel isolates routing only; positive mathematical/HTTP tests above
    # use the real solver and frozen oracle, with no mocks.
    for expression in ["abs(sin(x))>sqrt(2)/2", "abs(sin(x))<=sqrt(2)/2",
                       "abs(sin(x))>=1/2", "abs(cos(x))>=sqrt(2)/2", "sin(x)>=sqrt(2)/2"]:
        with patch("app.services.phase2_service.sympy.solve_univariate_inequality", return_value=sp.FiniteSet(12345)) as fallback:
            result = compute_inequality(parse_inequality_tree(expression), "x")
        fallback.assert_called_once()
        assert result.solution_set == sp.FiniteSet(12345)
        assert not result.warnings


def test_in_d05_preserves_constant_comparisons():
    assert compute_inequality(sp.S.true, "x").solution_set == sp.S.Reals
    assert compute_inequality(sp.S.false, "x").solution_set == sp.S.EmptySet
