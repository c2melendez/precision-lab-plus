"""SY-R-11 official rational inverse, exact two-sided HTTP product and reentry."""
import json,os
from pathlib import Path
import pytest
import sympy as sp
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS","http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse
rows=[json.loads(s) for s in (Path(__file__).resolve().parents[2]/"qa/certification/syntax309_cases.jsonl").read_text(encoding="utf-8").splitlines() if s.strip()]
A=[["-2","1"],["3/2","-1/2"]]
B=[["1","2"],["3","4"]]
def mat(cells): return sp.Matrix([[sp.sympify(v) for v in row] for row in cells])
def post(client,path,payload):
 response=client.post(path,json=payload)
 assert response.status_code==200,response.text
 result=MathResponse.model_validate(response.json())
 assert result.success and result.result_type.value=="matrix" and result.request_id,result
 assert result.result_data is not None and result.steps,result
 return result
def test_syr11_official_matrix_inverse_and_both_products_over_http():
 row=next(r for r in rows if r["id"]=="SY-R-11")
 assert row["entrada"]==r"\begin{pmatrix}-2&1\\\frac{3}{2}&-\frac{1}{2}\end{pmatrix}"
 assert row["operacion"]=="matriz" and "identidad" in row["esperado"]
 assert mat(A)*mat(B)==sp.eye(2) and mat(B)*mat(A)==sp.eye(2)
 with TestClient(app) as client:
  inv=post(client,"/api/v1/matrix/inverse",{"matrix":B})
  assert mat(inv.result_data)==mat(A)
  for left,right in [(A,B),(B,A),(inv.result_data,B),(B,inv.result_data)]:
   result=post(client,"/api/v1/matrix/operations",{"operation":"multiply","matrix_a":left,"matrix_b":right})
   assert mat(result.result_data)==sp.eye(2)
   assert result.result_data==[["1","0"],["0","1"]]
@pytest.mark.parametrize("altered",[
 [["-2","1"],["3/2","1/2"]],
 [["-2","1"],["2/3","-1/2"]],
 [["3/2","-1/2"],["-2","1"]],
])
def test_syr11_mutated_cells_are_not_inverse(altered):
 with TestClient(app) as client:
  result=post(client,"/api/v1/matrix/operations",{"operation":"multiply","matrix_a":altered,"matrix_b":B})
  assert mat(result.result_data)!=sp.eye(2)
