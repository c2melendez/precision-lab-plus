"""SY-M-18 exact HTTP transpose, shape and involution."""
import os
import pytest
import sympy as sp
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS","http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse
@pytest.mark.parametrize("matrix,expected",[
 ([["1","2"],["3","4"]],[["1","3"],["2","4"]]),
 ([["-1/2","2","3"],["4","5/3","-6"]],[["-1/2","4"],["2","5/3"],["3","-6"]]),
])
def test_sym18_exact_transpose_and_involution(matrix,expected):
 with TestClient(app) as client:
  response=client.post("/api/v1/matrix/transpose",json={"matrix":matrix})
  assert response.status_code==200,response.text
  result=MathResponse.model_validate(response.json())
  assert result.success and result.result_type.value=="matrix"
  actual=sp.Matrix([[sp.sympify(cell) for cell in row] for row in result.result_data])
  assert actual==sp.Matrix([[sp.sympify(cell) for cell in row] for row in expected])
  assert all(not value.has(sp.Float) for value in actual)
  again=client.post("/api/v1/matrix/transpose",json={"matrix":result.result_data})
  restored=MathResponse.model_validate(again.json())
  assert restored.success
  assert sp.Matrix([[sp.sympify(cell) for cell in row] for row in restored.result_data])==sp.Matrix([[sp.sympify(cell) for cell in row] for row in matrix])
