"""SY-M-17 exact HTTP inverse and independent identity witnesses."""
import os
import pytest
import sympy as sp
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS","http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse
def test_sym17_exact_inverse_and_both_identities():
 with TestClient(app) as client:
  response=client.post("/api/v1/matrix/inverse",json={"matrix":[["1","2"],["3","4"]]})
  assert response.status_code==200,response.text
  result=MathResponse.model_validate(response.json())
  assert result.success and result.result_type.value=="matrix"
  inverse=sp.Matrix([[sp.sympify(cell) for cell in row] for row in result.result_data])
  assert inverse==sp.Matrix([[-2,1],[sp.Rational(3,2),-sp.Rational(1,2)]])
  a=sp.Matrix([[1,2],[3,4]])
  assert a*inverse==sp.eye(2) and inverse*a==sp.eye(2)
  assert all(not value.has(sp.Float) for value in inverse)
@pytest.mark.parametrize("matrix,code",[
 ([["1","2"],["2","4"]],"SINGULAR_MATRIX"),
 ([["1","2","3"],["4","5","6"]],"DIMENSION_MISMATCH"),
])
def test_sym17_invalid_inverse_http(matrix,code):
 with TestClient(app) as client:
  response=client.post("/api/v1/matrix/inverse",json={"matrix":matrix})
  result=MathResponse.model_validate(response.json())
  assert not result.success and result.error_code.value==code
