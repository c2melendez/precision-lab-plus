"""SY-S-06 inverse tangent exact radians and reentry."""
import os
import pytest
import sympy as sp
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS","http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse
@pytest.mark.parametrize("expression",["atan(1)","atan((1))"])
def test_sys06_arctangent_http_exact(expression):
 with TestClient(app) as client:
  response=client.post("/api/v1/evaluate",json={"expression":expression,"angle_unit":"rad"})
  assert response.status_code==200,response.text
  result=MathResponse.model_validate(response.json())
  assert result.success,result
  assert sp.simplify(sp.sympify(result.result_text)-sp.pi/4)==0
  assert not sp.sympify(result.result_text).has(sp.Float)
  again=client.post("/api/v1/evaluate",json={"expression":result.result_text,"angle_unit":"rad"})
  assert again.status_code==200,again.text
  restored=MathResponse.model_validate(again.json())
  assert restored.success
  assert sp.simplify(sp.sympify(restored.result_text)-sp.pi/4)==0
