"""SY-Q-05: inconsistent equation produces contradiction, not identity or invented roots."""
import json
import os
from pathlib import Path
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS","http://localhost:5173")
from app.main import app
ROWS={r["id"]:r for r in (json.loads(line) for line in
 (Path(__file__).resolve().parents[2]/"qa/certification/syntax309_cases.jsonl")
 .read_text(encoding="utf-8").splitlines() if line.strip())}

def test_syq05_contradiction_and_identity_control():
 row=ROWS["SY-Q-05"]
 assert row["entrada"]=="x=x+1" and row["operacion"]=="resolver"
 with TestClient(app) as client:
  for equation, kind in (("x=x+1","contradiction"),("x+1=x","contradiction"),("x=x","identity")):
   response=client.post("/api/v1/solve",json={"equation":equation,"variable":"x"})
   assert response.status_code==200,response.text
   data=response.json()
   assert data["success"] is True,data
   assert data["result_type"]==kind,data
   assert data["has_detailed_steps"] is False,data
