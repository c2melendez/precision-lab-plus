"""IN-D-03: exact open interval on the frozen principal tangent branch."""
import gzip
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.parsing import parse_inequality_tree
from app.services.phase2_service import compute_inequality

EXPECTED = sp.Interval.open(-sp.pi / 2, sp.pi / 4)


def test_in_d03_source_row_is_frozen():
    source = gzip.decompress((Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/ejercicios_trigonometria.md.gz").read_bytes()).decode()
    row = next(line for line in source.splitlines() if "| IN-D-03 |" in line)
    assert [s.strip() for s in row.split("|") if s.strip()] == [
        "IN-D-03", r"`\tan x<1,\quad x\in\left(-\frac{\pi}{2},\frac{\pi}{2}\right)`",
        r"`\left(-\frac{\pi}{2},\frac{\pi}{4}\right)`",
    ]


def test_in_d03_service_returns_negative_part_and_excludes_pole_and_root():
    for expression, variable in [("tan(x)<1", "x"), ("1>tan(x)", "x"), ("tan(t)<1", "t")]:
        result = compute_inequality(parse_inequality_tree(expression), variable)
        assert result.solution_set == EXPECTED, result.solution_set
        assert result.solution_set.contains(-sp.pi/4) is sp.S.true
        assert result.solution_set.contains(-sp.pi/2) is sp.S.false
        assert result.solution_set.contains(sp.pi/4) is sp.S.false
        assert result.solution_set.contains(sp.pi/2) is sp.S.false
        assert result.warnings and "(-pi/2, pi/2)" in result.warnings[0]


def test_in_d03_http_returns_exact_interval_with_explicit_branch_scope():
    with TestClient(app) as client:
        response = client.post("/api/v1/inequality", json={"inequality": "tan(x)<1", "variable": "x"})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["operation"] == "inequality" and body["request_id"]
    assert body["result_text"] == "Interval.open(-pi/2, pi/4)"
    assert body["result_latex"] == sp.latex(EXPECTED)
    assert body["warnings"] and "(-pi/2, pi/2)" in body["warnings"][0]


def test_in_d03_independent_monotonic_branch_oracle():
    t = sp.Symbol("t", real=True)
    assert sp.atan(1) == sp.pi/4
    assert sp.diff(sp.tan(t), t) == sp.tan(t)**2 + 1
    for x, expected in [(-sp.pi/3, True), (-sp.pi/4, True), (0, True),
                        (sp.pi/6, True), (sp.pi/4, False), (sp.pi/3, False)]:
        assert bool(sp.tan(x) < 1) is expected
    assert sp.cos(-sp.pi/2) == 0 and sp.cos(sp.pi/2) == 0


def test_in_d03_preserves_unrelated_inequality_fallbacks():
    for expression in ["tan(x)<=1", "tan(x)<0", "tan(2*x)<1", "atan(x)<1", "tan(x)>1"]:
        result = compute_inequality(parse_inequality_tree(expression), "x")
        assert result.solution_set != EXPECTED
        assert not any("rama principal" in warning for warning in result.warnings)


def test_in_d03_preserves_constant_comparisons():
    assert compute_inequality(sp.S.true, "x").solution_set == sp.S.Reals
    assert compute_inequality(sp.S.false, "x").solution_set == sp.S.EmptySet
