"""SY-Q-21 real HTTP closed upper endpoint; source conversion tested separately."""
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
  assert result.input_text==expression and result.request_id
  assert result.result_text==str(expected)
  assert result.result_latex==sp.latex(expected)
  assert result.result_type.value=="scalar"
  return result

def test_syq21_source_and_exact_interval():
 row=ROWS["SY-Q-21"]
 assert row["entrada"]==r"x\leq2" and row["operacion"]=="resolver"
 assert row["esperado"]==r"x\in(-\infty,2]"
 # Explicit translation to this documented API channel; not a native UI claim.
 expression=row["entrada"].replace(r"\leq","<=")
 assert expression=="x<=2"
 expected=sp.Interval(-sp.oo,2)
 result=check(expression,expected)
 assert result.result_text=="Interval(-oo, 2)"
 assert expected.left_open and not expected.right_open
 assert [bool(expected.contains(x)) for x in [-1000000,1,2,3]]==[True,True,True,False]

@pytest.mark.parametrize("expression,expected",[
 ("x<2",sp.Interval.open(-sp.oo,2)),
 ("2>=x",sp.Interval(-sp.oo,2)),
 ("3*x<=6",sp.Interval(-sp.oo,2)),
 ("-x>=-2",sp.Interval(-sp.oo,2)),
 ("x<=3",sp.Interval(-sp.oo,3)),
])
def test_syq21_controls(expression,expected):
 check(expression,expected)
