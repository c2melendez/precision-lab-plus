"""SY-M-16 real HTTP typed payloads, separate from frontend source resolution."""
import os
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS","http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse
def test_sym16_matrix_determinant_and_scalar_abs_are_distinct():
 with TestClient(app) as client:
  matrix=MathResponse.model_validate(client.post("/api/v1/matrix/determinant",json={"matrix":[["1","2"],["3","4"]]}).json())
  scalar=MathResponse.model_validate(client.post("/api/v1/evaluate",json={"expression":"abs(-3)","angle_unit":"rad"}).json())
  assert matrix.success and matrix.result_text=="-2"
  assert scalar.success and scalar.result_text=="3"
  assert matrix.operation!=scalar.operation and matrix.request_id!=scalar.request_id
