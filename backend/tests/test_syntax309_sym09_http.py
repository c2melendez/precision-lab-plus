"""SY-M-09 real HTTP exact determinant, after frontend cell conversion."""
import os
import pytest
import sympy as sp
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS","http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse
@pytest.mark.parametrize("matrix,expected",[
 ([["1/2","sqrt(2)"],["pi","e"]],sp.E/2-sp.sqrt(2)*sp.pi),
 ([["pi","e"],["1/2","sqrt(2)"]],sp.sqrt(2)*sp.pi-sp.E/2),
 ([["1/2","sqrt(2)"],["1/2","sqrt(2)"]],sp.Integer(0)),
])
def test_sym09_exact_real_constant_determinant(matrix,expected):
 with TestClient(app) as client:
  response=client.post("/api/v1/matrix/determinant",json={"matrix":matrix})
  assert response.status_code==200,response.text
  result=MathResponse.model_validate(response.json())
  assert result.success,response.text
  assert sp.simplify(sp.sympify(result.result_text)-expected)==0
  assert result.result_latex==sp.latex(expected)
  assert abs(result.result_approx-float(expected))<1e-12
