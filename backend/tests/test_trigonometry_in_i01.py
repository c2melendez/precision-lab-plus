"""IN-I-01: strict inverse sine with real domain."""
import gzip
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.parsing import parse_inequality_tree
from app.services.phase2_service import compute_inequality

EXPECTED = sp.Interval.Lopen(sp.Rational(1,2), 1)

def test_source_row():
    source = gzip.decompress((Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/ejercicios_trigonometria.md.gz").read_bytes()).decode()
    row = next(line for line in source.splitlines() if "| IN-I-01 |" in line)
    assert [s.strip() for s in row.split("|") if s.strip()] == ["IN-I-01", r"`\arcsin x>\frac{\pi}{6}`", r"`\left(\frac{1}{2},1\right]`"]

def test_service():
    for expression, variable in [("asin(x)>pi/6", "x"), ("pi/6<asin(x)", "x"), ("asin(t)>pi/6", "t")]:
        result = compute_inequality(parse_inequality_tree(expression), variable)
        assert result.solution_set == EXPECTED
        assert result.solution_set.contains(sp.Rational(1,2)) is sp.S.false
        assert result.solution_set.contains(1) is sp.S.true
        assert result.solution_set.contains(2) is sp.S.false

def test_http():
    with TestClient(app) as client:
        response = client.post("/api/v1/inequality", json={"inequality":"asin(x)>pi/6", "variable":"x"})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] and body["operation"] == "inequality" and body["request_id"]
    assert body["result_text"] == str(EXPECTED) and body["result_latex"] == sp.latex(EXPECTED)

def test_domain_and_boundary():
    assert sp.asin(sp.Rational(1,2)) == sp.pi/6
    assert sp.asin(1) > sp.pi/6
    assert EXPECTED.contains(-1) is sp.S.false and EXPECTED.contains(1) is sp.S.true
