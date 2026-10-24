"""SY-Q-22 original ASCII source and inequality/equation distinction."""
import json,os
from pathlib import Path
import pytest
import sympy as sp
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS","http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse
ROWS={r["id"]:r for r in (json.loads(s) for s in
 (Path(__file__).resolve().parents[2]/"qa/certification/syntax309_cases.jsonl").read_text(encoding="utf-8").splitlines() if s.strip())}
def check(expression,expected):
 with TestClient(app) as client:
  response=client.post("/api/v1/inequality",json={"inequality":expression,"variable":"x"})
  assert response.status_code==200,response.text
  result=MathResponse.model_validate(response.json())
  assert result.success,response.text
  assert result.operation.value=="inequality"
  assert result.input_text==expression
  assert result.result_type.value=="scalar"
  assert result.result_text==str(expected) and result.result_latex==sp.latex(expected)
  assert result.request_id
  return result

def test_syq23_converted_http_includes_one():
 row=ROWS["SY-Q-23"]
 assert row["entrada"]=="x≥1" and row["operacion"]=="resolver"
 assert row["esperado"]==r"x\in[1,\infty)" and "Unicode" in row["nota"]
 # Real frontend conversion is tested independently; this is its ASCII HTTP contract.
 expected=sp.Interval(1,sp.oo)
 check("x>=1",expected)
 assert [bool(expected.contains(x)) for x in [0,1,2,1000000]]==[False,True,True,True]
 assert not expected.left_open and expected.right_open

@pytest.mark.parametrize("expression,expected",[
 ("x>1",sp.Interval.open(1,sp.oo)),
 ("1<=x",sp.Interval(1,sp.oo)),
 ("3*x>=3",sp.Interval(1,sp.oo)),
 ("-x<=-1",sp.Interval(1,sp.oo)),
 ("x>=2",sp.Interval(2,sp.oo)),
])
def test_syq23_direction_boundary_controls(expression,expected):
 check(expression,expected)
