"""SY-M-03 real HTTP determinant; frontend LaTeX extraction tested separately."""
import json,os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS","http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse
ROWS={r["id"]:r for r in (json.loads(s) for s in
 (Path(__file__).resolve().parents[2]/"qa/certification/syntax309_cases.jsonl").read_text(encoding="utf-8").splitlines() if s.strip())}

def check(matrix,expected):
 with TestClient(app) as client:
  response=client.post("/api/v1/matrix/determinant",json={"matrix":matrix})
  assert response.status_code==200,response.text
  result=MathResponse.model_validate(response.json())
  assert result.success,response.text
  assert result.operation.value=="matrix_determinant"
  assert result.result_type.value=="scalar"
  assert result.result_text==expected and result.result_latex==expected
  assert result.result_approx==float(expected)
  assert result.request_id and result.steps
  return result

def test_sym03_official_fixture_and_http_payload():
 row=ROWS["SY-M-03"]
 assert row["entrada"]==r"\begin{vmatrix}1&2\\3&4\end{vmatrix}"
 assert row["operacion"]=="det" and row["esperado"]=="-2"
 check([["1","2"],["3","4"]],row["esperado"])

@pytest.mark.parametrize("matrix,expected",[
 ([["3","4"],["1","2"]],"2"),
 ([["1","3"],["2","4"]],"-2"),
 ([["1","2"],["2","4"]],"0"),
 ([["1","2"],["3","5"]],"-1"),
])
def test_sym03_entry_and_orientation_controls(matrix,expected):
 check(matrix,expected)

def test_sym03_rectangular_determinant_rejected():
 with TestClient(app) as client:
  response=client.post("/api/v1/matrix/determinant",json={"matrix":[["1","2","3"],["4","5","6"]]})
  assert response.status_code==200,response.text
  result=MathResponse.model_validate(response.json())
  assert not result.success and result.error_code.value=="DIMENSION_MISMATCH"
