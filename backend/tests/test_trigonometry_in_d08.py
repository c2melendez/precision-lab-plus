"""IN-D-08: inclusive cotangent inequality on the principal branch (0, pi)."""
import gzip
from pathlib import Path
from unittest.mock import patch
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.parsing import parse_inequality_tree
from app.services.phase2_service import compute_inequality

EXPECTED = sp.Interval.Lopen(0, sp.pi / 4)

def test_source_row():
    source = gzip.decompress((Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/ejercicios_trigonometria.md.gz").read_bytes()).decode()
    row = next(line for line in source.splitlines() if "| IN-D-08 |" in line)
    assert [s.strip() for s in row.split("|") if s.strip()] == ["IN-D-08", r"`\cot x\ge 1,\quad x\in(0,\pi)`", r"`\left(0,\frac{\pi}{4}\right]`"]

def test_service():
    for expression, variable in [("cot(x)>=1", "x"), ("1<=cot(x)", "x"), ("cot(t)>=1", "t")]:
        result = compute_inequality(parse_inequality_tree(expression), variable)
        assert result.solution_set == EXPECTED
        assert result.solution_set.contains(0) is sp.S.false
        assert result.solution_set.contains(sp.pi / 4) is sp.S.true
        assert result.solution_set.contains(sp.pi / 8) is sp.S.true
        assert result.solution_set.contains(sp.pi / 2) is sp.S.false
        assert result.solution_set.contains(sp.pi) is sp.S.false
        assert not result.warnings

def test_http():
    with TestClient(app) as client:
        response = client.post("/api/v1/inequality", json={"inequality": "cot(x)>=1", "variable": "x"})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] and body["operation"] == "inequality" and body["request_id"]
    assert body["result_text"] == str(EXPECTED) and body["result_latex"] == sp.latex(EXPECTED)
    assert body["warnings"] == []

def test_independent_sign_and_poles():
    for k in [-1, 0, 1]:
        assert sp.simplify(sp.cot(sp.pi / 4 + k * sp.pi) - 1) == 0
    assert sp.cot(0) is sp.zoo and sp.cot(sp.pi) is sp.zoo
    assert sp.cot(sp.pi / 2) == 0
    for x, expected in [(sp.pi / 8, True), (sp.pi / 4, True), (sp.pi / 2, False), (3 * sp.pi / 4, False)]:
        assert bool(sp.cot(x) >= 1) is expected

def test_other_comparisons_keep_fallback():
    for expression in ["cot(x)>1", "cot(x)<=1", "cot(x)>=2", "cot(2*x)>=1", "cos(x)>=1"]:
        with patch("app.services.phase2_service.sympy.solve_univariate_inequality", return_value=sp.FiniteSet(12345)) as fallback:
            result = compute_inequality(parse_inequality_tree(expression), "x")
        fallback.assert_called_once()
        assert result.solution_set == sp.FiniteSet(12345) and not result.warnings

def test_constant_comparisons():
    assert compute_inequality(sp.S.true, "x").solution_set is sp.S.Reals
    assert compute_inequality(sp.S.false, "x").solution_set is sp.S.EmptySet
