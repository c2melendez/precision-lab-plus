"""IN-I-04: inclusive scaled inverse tangent on the real line."""
import gzip
from pathlib import Path
import sympy as sp
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.parsing import parse_inequality_tree
from app.services.phase2_service import compute_inequality

EXPECTED = sp.Interval(sp.Rational(1,2), sp.oo)

def test_source_row():
    source = gzip.decompress((Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/ejercicios_trigonometria.md.gz").read_bytes()).decode()
    row = next(line for line in source.splitlines() if "| IN-I-04 |" in line)
    assert [s.strip() for s in row.split("|") if s.strip()] == ["IN-I-04", r"`\arctan(2x)\ge\frac{\pi}{4}`", r"`\left[\frac{1}{2},\infty\right)`"]

def test_service():
    for expression, variable in [("atan(2*x)>=pi/4", "x"), ("pi/4<=atan(2*x)", "x"), ("atan(2*t)>=pi/4", "t")]:
        result = compute_inequality(parse_inequality_tree(expression), variable)
        assert result.solution_set == EXPECTED
        assert result.solution_set.contains(sp.Rational(1,2)) is sp.S.true
        assert result.solution_set.contains(0) is sp.S.false
        assert result.solution_set.contains(10) is sp.S.true

def test_http():
    with TestClient(app) as client:
        response = client.post("/api/v1/inequality", json={"inequality":"atan(2*x)>=pi/4", "variable":"x"})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] and body["operation"] == "inequality" and body["request_id"]
    assert body["result_text"] == str(EXPECTED) and body["result_latex"] == sp.latex(EXPECTED)

def test_source_literal_http():
    with TestClient(app) as client:
        response = client.post("/api/v1/inequality", json={"inequality":r"\arctan(2x)\ge\frac{\pi}{4}", "variable":"x"})
    assert response.status_code == 200
    body = response.json()
    assert body["success"], body
    assert body["result_text"] == str(EXPECTED) and body["result_latex"] == sp.latex(EXPECTED)

@pytest.mark.parametrize("text", [r"\arctan(2x)\ge\frac{\pi}{4};open(1)", r"\arctan(2x)\ge\frac{\pi}{4}=1", r"\arctan(2__import__(x))\ge\frac{\pi}{4}"])
def test_literal_path_rejects_unsafe_input(text):
    with pytest.raises((ValueError, TypeError)):
        parse_inequality_tree(text)

def test_boundary():
    assert sp.atan(1) == sp.pi/4
    assert sp.atan(sp.Rational(4,5)) < sp.pi/4 and sp.atan(2) > sp.pi/4
