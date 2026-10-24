"""SY-Q-17: public 1D inequality-system API, exact sets and open boundaries."""
import json
import os
from pathlib import Path
import pytest
import sympy as sp
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse

ROWS = {r["id"]:r for r in (json.loads(s) for s in
    (Path(__file__).resolve().parents[2]/"qa/certification/syntax309_cases.jsonl")
    .read_text(encoding="utf-8").splitlines() if s.strip())}

def check(rows, expected):
    with TestClient(app) as client:
        response=client.post("/api/v1/inequality/system",json={"inequalities":rows,"variables":["x"]})
        assert response.status_code==200,response.text
        result=MathResponse.model_validate(response.json())
        assert result.success,response.text
        assert result.operation.value=="inequality_system"
        assert result.result_type.value=="scalar"
        assert result.request_id
        assert result.input_text=="; ".join(rows)
        assert result.result_text==str(expected)
        assert result.result_latex==sp.latex(expected)
        return result

def test_syq17_official_source_open_interval():
    row=ROWS["SY-Q-17"]
    assert row["entrada"]==r"\begin{cases}x>1\\ x<3\end{cases}"
    assert row["esperado"]==r"x\in(1,3)"
    rows=row["entrada"][len(r"\begin{cases}"):-len(r"\end{cases}")].split(r"\\")
    rows=[r.strip() for r in rows]
    assert rows==["x>1","x<3"]
    first=check(rows,sp.Interval.open(1,3))
    second=check(list(reversed(rows)),sp.Interval.open(1,3))
    assert first.request_id!=second.request_id

@pytest.mark.parametrize("rows,expected",[
    (["x>=1","x<3"],sp.Interval.Ropen(1,3)),
    (["x>1","x<=3"],sp.Interval.Lopen(1,3)),
    (["x>=1","x<=3"],sp.Interval(1,3)),
    (["-2*x<-2","3*x<9"],sp.Interval.open(1,3)),
    (["x>0","x>=1","x<3","x<=4"],sp.Interval.Ropen(1,3)),
    (["x>1","x>=1"],sp.Interval.open(1,sp.oo)),
    (["x<3","x<=3"],sp.Interval.open(-sp.oo,3)),
    (["x>=2","x<=2"],sp.FiniteSet(2)),
    (["x>3","x<1"],sp.S.EmptySet),
    (["x>2","x<=2"],sp.S.EmptySet),
    (["x>=2","x<2"],sp.S.EmptySet),
    (["3*x>1","3*x<2"],sp.Interval.open(sp.Rational(1,3),sp.Rational(2,3))),
])
def test_syq17_boundaries_controls(rows,expected):
    check(rows,expected)

def test_syq17_does_not_ignore_other_variable():
    with TestClient(app) as client:
        response=client.post("/api/v1/inequality/system",json={"inequalities":["y>1","x<3"],"variables":["x"]})
        result=MathResponse.model_validate(response.json())
        assert not result.success,response.text
        assert result.error_code.value=="INVALID_VARIABLE"
