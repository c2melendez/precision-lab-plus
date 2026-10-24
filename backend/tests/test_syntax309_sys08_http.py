"""SY-S-08 official Spanish sinh numeric oracle through HTTP."""
import os
import math
import pytest
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS","http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse
@pytest.mark.parametrize("expression",["sinh(1)","sinh((1))"])
def test_sys08_sinh_http_numeric_and_reentry(expression):
 with TestClient(app) as client:
  response=client.post("/api/v1/evaluate",json={"expression":expression,"angle_unit":"rad"})
  assert response.status_code==200,response.text
  result=MathResponse.model_validate(response.json())
  assert result.success,result
  assert math.isclose(float(result.result_approx),1.175201194,rel_tol=0,abs_tol=5e-10)
  again=client.post("/api/v1/evaluate",json={"expression":result.result_text,"angle_unit":"rad"})
  assert again.status_code==200,again.text
  restored=MathResponse.model_validate(again.json())
  assert restored.success
  assert math.isclose(float(restored.result_approx),1.175201194,rel_tol=0,abs_tol=5e-10)
