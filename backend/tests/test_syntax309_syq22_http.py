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

def test_syq22_original_ascii_source_includes_two():
 row=ROWS["SY-Q-22"]
 assert row["entrada"]=="x<=2" and row["operacion"]=="resolver"
 assert row["esperado"]==r"x\in(-\infty,2]" and "ASCII" in row["nota"]
 expected=sp.Interval(-sp.oo,2)
 check(row["entrada"],expected)
 assert [bool(expected.contains(x)) for x in [-1000000,1,2,3]]==[True,True,True,False]
 assert expected.left_open and not expected.right_open

@pytest.mark.parametrize("expression,expected",[
 ("x <= 2",sp.Interval(-sp.oo,2)),
 ("2>=x",sp.Interval(-sp.oo,2)),
 ("x<2",sp.Interval.open(-sp.oo,2)),
 ("3*x<=6",sp.Interval(-sp.oo,2)),
])
def test_syq22_ascii_controls(expression,expected):
 check(expression,expected)

def test_syq22_equality_has_a_different_operation_and_solution_type():
 inequality=check("x<=2",sp.Interval(-sp.oo,2))
 with TestClient(app) as client:
  response=client.post("/api/v1/solve",json={"equation":"x=2","variable":"x"})
  result=MathResponse.model_validate(response.json())
  assert result.success,response.text
  assert result.operation.value=="solve" and result.result_type.value=="equation_solutions"
  assert len(result.result_data)==1 and result.result_data[0].text=="2"
  assert result.request_id!=inequality.request_id
