"""SY-S-05 exact arcsine result and reentry through public endpoint."""
import os
import pytest
import sympy as sp
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS","http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse
@pytest.mark.parametrize("expression",["asin(1/2)","asin((1)/(2))"])
def test_sys05_exact_arcsine_http(expression):
 with TestClient(app) as client:
  response=client.post("/api/v1/evaluate",json={"expression":expression,"angle_unit":"rad"})
  assert response.status_code==200,response.text
  result=MathResponse.model_validate(response.json())
  assert result.success,result
  assert sp.simplify(sp.sympify(result.result_text)-sp.pi/6)==0,result
  assert not sp.sympify(result.result_text).has(sp.Float)
  again=client.post("/api/v1/evaluate",json={"expression":result.result_text,"angle_unit":"rad"})
  assert again.status_code==200,again.text
  restored=MathResponse.model_validate(again.json())
  assert restored.success
  assert sp.simplify(sp.sympify(restored.result_text)-sp.pi/6)==0
