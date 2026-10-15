"""SY-Q-01 exact quadratic solve via actual Plus HTTP /solve."""
import json
import os
from pathlib import Path
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
ROWS = {r["id"]: r for r in (json.loads(line) for line in
    (Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl")
    .read_text(encoding="utf-8").splitlines() if line.strip())}

def test_syq01_two_quadratic_roots_and_reversed_form():
    row = ROWS["SY-Q-01"]
    assert row["entrada"] == "x^{2}=4" and row["operacion"] == "resolver"
    with TestClient(app) as client:
        for equation in ("x^2=4", "4=x^2"):
            response = client.post("/api/v1/solve", json={"equation": equation, "variable": "x"})
            assert response.status_code == 200, response.text
            data = response.json()
            assert data["success"] is True, data
            roots = sorted(float(solution["text"]) for solution in data["result_data"])
            assert roots == [-2.0, 2.0], data
            assert all(x*x == 4 for x in roots)
