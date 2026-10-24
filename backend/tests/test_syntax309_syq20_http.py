"""SY-Q-20 /solve declares zero RHS; /evaluate remains expression evaluation."""
import json,os
from pathlib import Path
import pytest
import sympy as sp
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS","http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse
WARNING="Sin signo =: en Resolver se interpreta la expresión como una ecuación igual a 0."
ROWS={r["id"]:r for r in (json.loads(s) for s in
 (Path(__file__).resolve().parents[2]/"qa/certification/syntax309_cases.jsonl").read_text(encoding="utf-8").splitlines() if s.strip())}

def test_syq20_implicit_zero_declared_and_equivalent_to_explicit_zero():
 row=ROWS["SY-Q-20"]
 assert row["entrada"]==r"x^{2}-4" and row["operacion"]=="convencion"
 assert "=0" in row["esperado"]
 # Explicit source translation for the backend channel, not a native editor proof.
 expression=row["entrada"].replace("{","(").replace("}",")")
 assert expression=="x^(2)-4"
 with TestClient(app) as client:
  replies=[]
  for equation in [expression,expression+"=0"]:
   response=client.post("/api/v1/solve",json={"equation":equation,"variable":"x"})
   assert response.status_code==200,response.text
   result=MathResponse.model_validate(response.json())
   assert result.success,response.text
   assert result.operation.value=="solve" and result.result_type.value=="equation_solutions"
   assert result.input_text==equation and "=" in result.input_latex
   assert len(result.result_data)==2
   assert {s.text for s in result.result_data}=={"-2","2"}
   replies.append(result)
  assert WARNING in replies[0].warnings and WARNING not in replies[1].warnings
  assert replies[0].request_id!=replies[1].request_id
  for root in replies[0].result_data:
   replay=client.post("/api/v1/solve",json={"equation":"x="+root.text,"variable":"x"})
   replay_result=MathResponse.model_validate(replay.json())
   assert replay_result.success,replay.text
   assert [s.text for s in replay_result.result_data]==[root.text]
   assert replay_result.request_id!=replies[0].request_id

def test_syq20_evaluate_does_not_solve_or_impose_zero():
 with TestClient(app) as client:
  response=client.post("/api/v1/evaluate",json={"expression":"x^2-4"})
  result=MathResponse.model_validate(response.json())
  assert result.success,response.text
  assert result.operation.value=="evaluate"
  x=sp.Symbol("x")
  assert sp.simplify(sp.sympify(result.result_text)-(x*x-4))==0
  assert sp.sympify(result.result_text).free_symbols=={x}
  assert WARNING not in result.warnings

@pytest.mark.parametrize("expression,kind",[("0","identity"),("1","contradiction"),("x-x","identity")])
def test_syq20_implicit_zero_is_declared_even_for_early_truth_results(expression,kind):
 with TestClient(app) as client:
  response=client.post("/api/v1/solve",json={"equation":expression})
  result=MathResponse.model_validate(response.json())
  assert result.success,response.text
  assert result.result_type.value==kind
  assert WARNING in result.warnings
