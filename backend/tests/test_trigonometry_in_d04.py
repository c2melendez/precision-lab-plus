"""IN-D-04: three exact components, scoped to [0,2*pi), not just the first arc."""
import gzip
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.parsing import parse_inequality_tree
from app.services.phase2_service import compute_inequality

EXPECTED = sp.Union(sp.Interval.Ropen(0, sp.pi/2), sp.Interval.open(sp.pi/2, 7*sp.pi/6),
                    sp.Interval.open(11*sp.pi/6, 2*sp.pi))


def test_in_d04_source_row_is_frozen():
    source = gzip.decompress((Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/ejercicios_trigonometria.md.gz").read_bytes()).decode()
    row = next(line for line in source.splitlines() if "| IN-D-04 |" in line)
    assert [s.strip() for s in row.split("|") if s.strip()] == [
        "IN-D-04", r"`2\sin^{2}x-\sin x-1<0,\quad x\in[0,2\pi)`",
        r"`\left[0,\frac{\pi}{2}\right)\cup\left(\frac{\pi}{2},\frac{7\pi}{6}\right)\cup\left(\frac{11\pi}{6},2\pi\right)`",
    ]


def test_in_d04_service_returns_all_three_components_and_exact_boundary_membership():
    for expression, var in [("2*sin(x)^2-sin(x)-1<0", "x"),
                            ("0>2*sin(x)^2-sin(x)-1", "x"), ("2*sin(t)^2-sin(t)-1<0", "t")]:
        result = compute_inequality(parse_inequality_tree(expression), var)
        assert result.solution_set == EXPECTED, result.solution_set
        assert result.solution_set.contains(0) is sp.S.true
        for boundary in [sp.pi/2, 7*sp.pi/6, 11*sp.pi/6, 2*sp.pi]:
            assert result.solution_set.contains(boundary) is sp.S.false
        for value in [sp.pi/4, sp.pi, 23*sp.pi/12]:
            assert result.solution_set.contains(value) is sp.S.true
        assert result.solution_set.contains(3*sp.pi/2) is sp.S.false
        assert result.warnings and "[0, 2*pi)" in result.warnings[0]


def test_in_d04_http_returns_exact_union_and_explicit_period_scope():
    with TestClient(app) as client:
        response = client.post("/api/v1/inequality", json={"inequality": "2*sin(x)^2-sin(x)-1<0", "variable": "x"})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    assert body["operation"] == "inequality" and body["request_id"]
    assert body["result_text"] == str(EXPECTED)
    assert body["result_latex"] == sp.latex(EXPECTED)
    assert body["warnings"] and "[0, 2*pi)" in body["warnings"][0]


def test_in_d04_independent_factored_polynomial_and_exact_sign_oracle():
    y = sp.Symbol("y", real=True)
    assert sp.expand((2*y+1)*(y-1)) == 2*y**2-y-1
    for angle, expected in [(0, True), (sp.pi/4, True), (sp.pi/2, False), (sp.pi, True),
                            (7*sp.pi/6, False), (3*sp.pi/2, False), (11*sp.pi/6, False), (23*sp.pi/12, True)]:
        value = 2*sp.sin(angle)**2-sp.sin(angle)-1
        assert bool(sp.simplify(value) < 0) is expected


def test_in_d04_preserves_unrelated_comparisons_and_constant_booleans():
    for expression in ["2*sin(x)^2-sin(x)-1<=0", "2*sin(x)^2-sin(x)-1>0", "2*sin(x)^2-sin(x)-2<0"]:
        result = compute_inequality(parse_inequality_tree(expression), "x")
        assert not any("[0, 2*pi)" in warning for warning in result.warnings)
    assert compute_inequality(sp.S.true, "x").solution_set == sp.S.Reals
    assert compute_inequality(sp.S.false, "x").solution_set == sp.S.EmptySet
