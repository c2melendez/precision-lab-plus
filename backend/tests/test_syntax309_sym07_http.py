"""SY-M-07: malformed matrix payload is a clear HTTP error; corrected payload recovers."""
import json,os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS","http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse
ROWS={r["id"]:r for r in (json.loads(s) for s in
 (Path(__file__).resolve().parents[2]/"qa/certification/syntax309_cases.jsonl").read_text(encoding="utf-8").splitlines() if s.strip())}
def test_sym07_official_fixture():
 row=ROWS["SY-M-07"]
 assert row["entrada"]==r"\begin{pmatrix}1&2\\3\end{pmatrix}"
 assert row["operacion"]=="error" and "filas de distinta longitud" in row["esperado"]
@pytest.mark.parametrize("matrix",[[["1","2"],["3"]],[["1"],["2","3"]]])
def test_sym07_rejects_unequal_rows_and_recovers(matrix):
 with TestClient(app) as client:
  response=client.post("/api/v1/matrix/determinant",json={"matrix":matrix})
  assert response.status_code==200,response.text
  result=MathResponse.model_validate(response.json())
  assert not result.success and result.error_code.value=="PARSE_ERROR"
  assert "filas" in result.error_message and "longitud" in result.error_message
  fixed=client.post("/api/v1/matrix/determinant",json={"matrix":[["1","2"],["3","4"]]})
  answer=MathResponse.model_validate(fixed.json())
  assert answer.success and answer.result_text=="-2"
  assert answer.request_id!=result.request_id
