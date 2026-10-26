"""SY-M-20 exact scalar matrix multiplication via kI * A."""
import os
import pytest
import sympy as sp
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS","http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse
@pytest.mark.parametrize("scalar,matrix,expected",[
 ("2",[["1","2"],["3","4"]],[["2","4"],["6","8"]]),
 ("-1/2",[["1","-2","3"],["4","5","6"]],[["-1/2","1","-3/2"],["-2","-5/2","-3"]]),
 ("0",[["1","-2","3"],["4","5","6"]],[["0","0","0"],["0","0","0"]]),
])
def test_sym20_exact_scale_http(scalar,matrix,expected):
 diagonal=[[scalar if r==c else "0" for c in range(len(matrix))] for r in range(len(matrix))]
 with TestClient(app) as client:
  response=client.post("/api/v1/matrix/operations",json={"operation":"multiply","matrix_a":diagonal,"matrix_b":matrix})
  assert response.status_code==200,response.text
  result=MathResponse.model_validate(response.json())
  assert result.success and result.result_type.value=="matrix"
  actual=sp.Matrix([[sp.sympify(cell) for cell in row] for row in result.result_data])
  assert actual==sp.Matrix([[sp.sympify(cell) for cell in row] for row in expected])
  assert actual.shape==(len(matrix),len(matrix[0]))
  assert all(not value.has(sp.Float) for value in actual)
