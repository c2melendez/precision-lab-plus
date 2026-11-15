"""IN-D-09 strict cosecant on [0, 2*pi)."""
import gzip
from pathlib import Path
from unittest.mock import patch
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.parsing import parse_inequality_tree
from app.services.phase2_service import compute_inequality

EXPECTED = sp.Union(sp.Interval.open(sp.pi, 7*sp.pi/6), sp.Interval.open(11*sp.pi/6, 2*sp.pi))

def test_source_row():
    source = gzip.decompress((Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/ejercicios_trigonometria.md.gz").read_bytes()).decode()
    row = next(line for line in source.splitlines() if "| IN-D-09 |" in line)
    assert [s.strip() for s in row.split("|") if s.strip()] == ["IN-D-09", r"`\csc x<-2,\quad x\in[0,2\pi)`", r"`\left(\pi,\frac{7\pi}{6}\right)\cup\left(\frac{11\pi}{6},2\pi\right)`"]

def test_service():
    for expression, variable in [("csc(x)<-2", "x"), ("-2>csc(x)", "x"), ("csc(t)<-2", "t")]:
        result = compute_inequality(parse_inequality_tree(expression), variable)
        assert result.solution_set == EXPECTED
        for boundary in [sp.pi, 7*sp.pi/6, 11*sp.pi/6, 2*sp.pi]: assert result.solution_set.contains(boundary) is sp.S.false
        assert result.warnings and "[0, 2*pi)" in result.warnings[0]

def test_http():
    with TestClient(app) as client:
        response = client.post("/api/v1/inequality", json={"inequality":"csc(x)<-2", "variable":"x"})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] and body["operation"] == "inequality" and body["request_id"]
    assert body["result_text"] == str(EXPECTED) and body["result_latex"] == sp.latex(EXPECTED)
    assert "[0, 2*pi)" in body["warnings"][0]

def test_signs_and_poles():
    assert sp.csc(sp.pi) is sp.zoo and sp.csc(2*sp.pi) is sp.zoo
    for x in [7*sp.pi/6, 11*sp.pi/6]: assert sp.csc(x) == -2
    for x, expected in [(13*sp.pi/12,True),(3*sp.pi/2,False),(23*sp.pi/12,True)]: assert bool(sp.csc(x)<-2) is expected

def test_fallback():
    for expression in ["csc(x)<=-2", "csc(x)<-3", "csc(2*x)<-2", "sin(x)<-2"]:
        with patch("app.services.phase2_service.sympy.solve_univariate_inequality", return_value=sp.FiniteSet(12345)) as fallback:
            result = compute_inequality(parse_inequality_tree(expression), "x")
        fallback.assert_called_once()
        assert result.solution_set == sp.FiniteSet(12345) and not result.warnings
