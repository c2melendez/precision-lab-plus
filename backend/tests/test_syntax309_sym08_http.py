"""SY-M-08 empty matrix contracts, distinct from explicit zeros."""
import json,os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS","http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse
ROWS={r["id"]:r for r in (json.loads(s) for s in
 (Path(__file__).resolve().parents[2]/"qa/certification/syntax309_cases.jsonl").read_text(encoding="utf-8").splitlines() if s.strip())}
def test_sym08_official_fixture():
 row=ROWS["SY-M-08"]
 assert row["entrada"]==r"\begin{pmatrix}\end{pmatrix}"
 assert row["operacion"]=="error" and "matriz vacía" in row["esperado"]
@pytest.mark.parametrize("matrix",[[[]],[[],[]]])
def test_sym08_empty_rows_rejected_and_recovery(matrix):
 with TestClient(app) as client:
  response=client.post("/api/v1/matrix/determinant",json={"matrix":matrix})
  assert response.status_code==200,response.text
  result=MathResponse.model_validate(response.json())
  assert not result.success and result.error_code.value=="PARSE_ERROR"
  assert "matriz" in result.error_message and "vacía" in result.error_message
  fixed=client.post("/api/v1/matrix/determinant",json={"matrix":[["1","2"],["3","4"]]})
  answer=MathResponse.model_validate(fixed.json())
  assert answer.success and answer.result_text=="-2"
def test_sym08_outer_empty_list_rejected_by_existing_schema():
 with TestClient(app) as client:
  response=client.post("/api/v1/matrix/determinant",json={"matrix":[]})
  assert response.status_code==422,response.text
  assert "matrix" in response.text
def test_sym08_explicit_zeros_are_valid():
 with TestClient(app) as client:
  response=client.post("/api/v1/matrix/determinant",json={"matrix":[["0","0"],["0","0"]]})
  result=MathResponse.model_validate(response.json())
  assert result.success and result.result_text=="0"
