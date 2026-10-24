"""SY-S-01 sine witness: explicit UI translation and exact HTTP reentry."""
import os
import pytest
import sympy as sp
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS","http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse
@pytest.mark.parametrize("expression",["sin(pi/6)","sin((pi)/(6))"])
def test_sys01_sine_exact_http_and_reentry(expression):
 with TestClient(app) as client:
  response=client.post("/api/v1/evaluate",json={"expression":expression,"angle_unit":"rad"})
  assert response.status_code==200,response.text
  result=MathResponse.model_validate(response.json())
  assert result.success and result.result_type.value=="scalar",result
  assert sp.sympify(result.result_text)==sp.Rational(1,2)
  assert not sp.sympify(result.result_text).has(sp.Float)
  assert result.result_latex==r"\frac{1}{2}"
  assert result.result_approx==0.5
  again=client.post("/api/v1/evaluate",json={"expression":result.result_text,"angle_unit":"rad"})
  restored=MathResponse.model_validate(again.json())
  assert restored.success and sp.sympify(restored.result_text)==sp.Rational(1,2)
