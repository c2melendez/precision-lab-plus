"""IN-I-05: inverse sine less than inverse cosine on their real domain."""
import gzip
from pathlib import Path
import sympy as sp
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.services.parsing import parse_inequality_tree
from app.services.phase2_service import compute_inequality

EXPECTED = sp.Interval.Ropen(-1, sp.sqrt(2)/2)

def test_source_row():
    source = gzip.decompress((Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/ejercicios_trigonometria.md.gz").read_bytes()).decode()
    row = next(line for line in source.splitlines() if "| IN-I-05 |" in line)
    assert [s.strip() for s in row.split("|") if s.strip()] == ["IN-I-05", r"`\arcsin x<\arccos x`", r"`\left[-1,\frac{\sqrt{2}}{2}\right)`"]

def test_service():
    for expression, variable in [("asin(x)<acos(x)", "x"), ("acos(x)>asin(x)", "x"), ("asin(t)<acos(t)", "t")]:
        result = compute_inequality(parse_inequality_tree(expression), variable)
        assert result.solution_set == EXPECTED
        assert result.solution_set.contains(-1) is sp.S.true
        assert result.solution_set.contains(sp.sqrt(2)/2) is sp.S.false
        assert result.solution_set.contains(1) is sp.S.false
        assert result.solution_set.contains(-2) is sp.S.false

def test_http():
    with TestClient(app) as client:
        response = client.post("/api/v1/inequality", json={"inequality":"asin(x)<acos(x)", "variable":"x"})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] and body["operation"] == "inequality" and body["request_id"]
    assert body["result_text"] == str(EXPECTED) and body["result_latex"] == sp.latex(EXPECTED)

def test_source_literal_http():
    with TestClient(app) as client:
        response = client.post("/api/v1/inequality", json={"inequality":r"\arcsin x<\arccos x", "variable":"x"})
    assert response.status_code == 200
    body = response.json()
    assert body["success"], body
    assert body["result_text"] == str(EXPECTED) and body["result_latex"] == sp.latex(EXPECTED)

@pytest.mark.parametrize("text", [r"\arcsin x<\arccos x;open(1)", r"\arcsin x<\arccos x=1", r"\arcsin __import__(x)<\arccos x"])
def test_literal_path_rejects_unsafe_input(text):
    with pytest.raises((ValueError, TypeError)):
        parse_inequality_tree(text)

def test_boundary():
    assert sp.asin(sp.sqrt(2)/2) == sp.acos(sp.sqrt(2)/2) == sp.pi/4
    assert sp.asin(-1) < sp.acos(-1) and sp.asin(1) > sp.acos(1)

def test_other_comparisons_keep_fallback():
    for expression in ["asin(x)<=acos(x)", "asin(x)>acos(x)", "asin(2*x)<acos(x)"]:
        with patch("app.services.phase2_service.sympy.solve_univariate_inequality", return_value=sp.FiniteSet(12345)) as fallback:
            result = compute_inequality(parse_inequality_tree(expression), "x")
        fallback.assert_called_once()
        assert result.solution_set == sp.FiniteSet(12345) and not result.warnings
