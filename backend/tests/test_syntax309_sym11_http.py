"""SY-M-11 real HTTP dot product; frontend matrix intent tested independently."""
import os
import pytest
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS","http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse
@pytest.mark.parametrize("a,b,expected",[
 ([["1"],["2"],["3"]],[["4"],["5"],["6"]],"32"),
 ([["1","2","3"]],[["4","5","6"]],"32"),
 ([["1"],["2"],["3"]],[["-4"],["-5"],["-6"]],"-32"),
])
def test_sym11_dot_http(a,b,expected):
 with TestClient(app) as client:
  response=client.post("/api/v1/matrix/operations",json={"operation":"dot","matrix_a":a,"matrix_b":b})
  assert response.status_code==200,response.text
  result=MathResponse.model_validate(response.json())
  assert result.success,response.text
  assert result.result_type.value=="scalar" and result.result_text==expected
  assert result.result_latex==expected and result.result_approx==float(expected)
def test_sym11_rejects_unequal_lengths():
 with TestClient(app) as client:
  response=client.post("/api/v1/matrix/operations",json={"operation":"dot","matrix_a":[["1"],["2"]],"matrix_b":[["3"]]})
  result=MathResponse.model_validate(response.json())
  assert not result.success and result.error_code.value=="DIMENSION_MISMATCH"
