"""IN-D-07: strict secant inequality on the principal branch."""
import gzip
from pathlib import Path
from unittest.mock import patch
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.parsing import parse_inequality_tree
from app.services.phase2_service import compute_inequality

EXPECTED = sp.Union(sp.Interval.open(-sp.pi/2, -sp.pi/3), sp.Interval.open(sp.pi/3, sp.pi/2))

def test_source_row():
    source = gzip.decompress((Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/ejercicios_trigonometria.md.gz").read_bytes()).decode()
    row = next(line for line in source.splitlines() if "| IN-D-07 |" in line)
    assert [s.strip() for s in row.split("|") if s.strip()] == ["IN-D-07", r"`\sec x>2,\quad x\in\left(-\frac{\pi}{2},\frac{\pi}{2}\right)`", r"`\left(-\frac{\pi}{2},-\frac{\pi}{3}\right)\cup\left(\frac{\pi}{3},\frac{\pi}{2}\right)`"]

def test_service():
    for expression, variable in [("sec(x)>2", "x"), ("2<sec(x)", "x"), ("sec(t)>2", "t")]:
        result = compute_inequality(parse_inequality_tree(expression), variable)
        assert result.solution_set == EXPECTED
        for boundary in [-sp.pi/2, -sp.pi/3, sp.pi/3, sp.pi/2]:
            assert result.solution_set.contains(boundary) is sp.S.false
        assert result.warnings and "(-pi/2, pi/2)" in result.warnings[0]

def test_http():
    with TestClient(app) as client:
        response = client.post("/api/v1/inequality", json={"inequality":"sec(x)>2", "variable":"x"})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] and body["operation"] == "inequality" and body["request_id"]
    assert body["result_text"] == str(EXPECTED) and body["result_latex"] == sp.latex(EXPECTED)
    assert "(-pi/2, pi/2)" in body["warnings"][0]

def test_independent_sign_and_poles():
    for x, expected in [(-5*sp.pi/12, True),(-sp.pi/3, False),(0, False),(sp.pi/3, False),(5*sp.pi/12, True)]:
        assert bool(sp.sec(x)>2) is expected
    assert sp.cos(-sp.pi/2) == 0 and sp.cos(sp.pi/2) == 0

def test_other_comparisons_keep_fallback():
    for expression in ["sec(x)>=2", "sec(x)<2", "sec(x)>3", "sec(2*x)>2", "cos(x)>2"]:
        with patch("app.services.phase2_service.sympy.solve_univariate_inequality", return_value=sp.FiniteSet(12345)) as fallback:
            result = compute_inequality(parse_inequality_tree(expression), "x")
        fallback.assert_called_once()
        assert result.solution_set == sp.FiniteSet(12345) and not result.warnings

def test_constant_comparisons():
    assert compute_inequality(sp.S.true, "x").solution_set is sp.S.Reals
    assert compute_inequality(sp.S.false, "x").solution_set is sp.S.EmptySet
