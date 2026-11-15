"""IN-D-06: sine-cosine inequality over one frozen period."""
import gzip
from pathlib import Path
from unittest.mock import patch
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.parsing import parse_inequality_tree
from app.services.phase2_service import compute_inequality

EXPECTED = sp.Union(sp.Interval.open(0, sp.pi/2), sp.Interval.open(sp.pi, 3*sp.pi/2))

def test_source_row():
    source = gzip.decompress((Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/ejercicios_trigonometria.md.gz").read_bytes()).decode()
    row = next(line for line in source.splitlines() if "| IN-D-06 |" in line)
    assert [s.strip() for s in row.split("|") if s.strip()] == ["IN-D-06", r"`\sin x\cos x>0,\quad x\in[0,2\pi)`", r"`\left(0,\frac{\pi}{2}\right)\cup\left(\pi,\frac{3\pi}{2}\right)`"]

def test_service():
    for expression, variable in [("sin(x)*cos(x)>0", "x"), ("0<sin(x)*cos(x)", "x"), ("sin(t)*cos(t)>0", "t")]:
        result = compute_inequality(parse_inequality_tree(expression), variable)
        assert result.solution_set == EXPECTED
        assert all(result.solution_set.contains(v) is sp.S.false for v in [0, sp.pi/2, sp.pi, 3*sp.pi/2, 2*sp.pi])
        assert result.warnings and "[0, 2*pi)" in result.warnings[0]

def test_http():
    with TestClient(app) as client:
        response = client.post("/api/v1/inequality", json={"inequality":"sin(x)*cos(x)>0", "variable":"x"})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] and body["operation"] == "inequality" and body["request_id"]
    assert body["result_text"] == str(EXPECTED)
    assert body["result_latex"] == sp.latex(EXPECTED)
    assert "[0, 2*pi)" in body["warnings"][0]

def test_independent_oracle():
    for value, expected in [(0, False), (sp.pi/4, True), (sp.pi/2, False), (3*sp.pi/4, False), (sp.pi, False), (5*sp.pi/4, True), (3*sp.pi/2, False), (7*sp.pi/4, False), (2*sp.pi, False)]:
        assert bool(sp.sin(value)*sp.cos(value)>0) is expected

def test_nonmatching_comparisons_preserve_fallback():
    for expression in ["sin(x)*cos(x)>=0", "sin(x)*cos(x)<0", "sin(2*x)*cos(x)>0", "sin(x)*cos(x)>1"]:
        with patch("app.services.phase2_service.sympy.solve_univariate_inequality", return_value=sp.FiniteSet(12345)) as fallback:
            result = compute_inequality(parse_inequality_tree(expression), "x")
        fallback.assert_called_once()
        assert result.solution_set == sp.FiniteSet(12345) and not result.warnings

def test_constant_comparisons():
    assert compute_inequality(sp.S.true, "x").solution_set == sp.S.Reals
    assert compute_inequality(sp.S.false, "x").solution_set == sp.S.EmptySet
