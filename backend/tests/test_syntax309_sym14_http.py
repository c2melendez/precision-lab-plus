"""SY-M-14 actual HTTP dot contract after local declaration extraction."""
import os
import pytest
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS","http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse
@pytest.mark.parametrize("a,b,expected",[
 ([["1","2","3"]],[["4","5","6"]],"32"),
 ([["1","2","3"]],[["0","1","0"]],"2"),
 ([["4","5","6"]],[["1","2","3"]],"32"),
])
def test_sym14_http_declared_payload(a,b,expected):
 with TestClient(app) as client:
  response=client.post("/api/v1/matrix/operations",json={"operation":"dot","matrix_a":a,"matrix_b":b})
  assert response.status_code==200,response.text
  result=MathResponse.model_validate(response.json())
  assert result.success and result.result_text==expected and result.result_type.value=="scalar"
