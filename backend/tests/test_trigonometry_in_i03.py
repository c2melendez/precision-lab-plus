"""IN-I-03: strict inverse tangent on the real line."""
import gzip
from pathlib import Path
import sympy as sp
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.parsing import parse_inequality_tree
from app.services.phase2_service import compute_inequality

EXPECTED = sp.Interval.open(-sp.oo, sp.tan(1))

def test_source_row():
    source = gzip.decompress((Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/ejercicios_trigonometria.md.gz").read_bytes()).decode()
    row = next(line for line in source.splitlines() if "| IN-I-03 |" in line)
    assert [s.strip() for s in row.split("|") if s.strip()] == ["IN-I-03", r"`\arctan x<1`", r"`\left(-\infty,\tan 1\right)` con `\tan 1\approx 1.557407725`"]

def test_service():
    for expression, variable in [("atan(x)<1", "x"), ("1>atan(x)", "x"), ("atan(t)<1", "t")]:
        result = compute_inequality(parse_inequality_tree(expression), variable)
        assert result.solution_set == EXPECTED
        assert result.solution_set.contains(sp.tan(1)) is sp.S.false
        assert result.solution_set.contains(1) is sp.S.true
        assert result.solution_set.contains(2) is sp.S.false

def test_http():
    with TestClient(app) as client:
        response = client.post("/api/v1/inequality", json={"inequality":"atan(x)<1", "variable":"x"})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] and body["operation"] == "inequality" and body["request_id"]
    assert body["result_text"] == str(EXPECTED) and body["result_latex"] == sp.latex(EXPECTED)

def test_source_literal_http():
    with TestClient(app) as client:
        response = client.post("/api/v1/inequality", json={"inequality":r"\arctan x<1", "variable":"x"})
    assert response.status_code == 200
    body = response.json()
    assert body["success"], body
    assert body["result_text"] == str(EXPECTED) and body["result_latex"] == sp.latex(EXPECTED)

@pytest.mark.parametrize("text", [r"\arctan x<1;open(1)", r"\arctan x<1=1", r"\arctan __import__(x)<1"])
def test_literal_path_does_not_accept_trailing_or_unsafe_input(text):
    with pytest.raises((ValueError, TypeError)):
        parse_inequality_tree(text)

def test_boundary():
    assert sp.atan(sp.tan(1)) == 1
    assert abs(float(sp.tan(1))-1.557407725) < 1e-9
