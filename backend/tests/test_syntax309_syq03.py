"""SY-Q-03: preserve roots when unknown is on RHS via real HTTP solve."""
import json
import os
from pathlib import Path
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
ROWS = {r["id"]: r for r in (json.loads(line) for line in
    (Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl")
    .read_text(encoding="utf-8").splitlines() if line.strip())}

def test_syq03_right_hand_unknown_equivalence():
    row = ROWS["SY-Q-03"]
    assert row["entrada"] == "4=x^{2}" and row["operacion"] == "resolver"
    assert "derecho" in row["nota"]
    with TestClient(app) as client:
        results = []
        for equation in ("4=x^2", "x^2=4", "x^2-4=0"):
            response = client.post("/api/v1/solve", json={"equation": equation, "variable": "x"})
            assert response.status_code == 200, response.text
            data = response.json()
            assert data["success"] is True, data
            roots = sorted(float(s["text"]) for s in data["result_data"])
            assert roots == [-2.0, 2.0], data
            assert all(4 - x*x == 0 for x in roots)
            results.append(roots)
        assert results[0] == results[1] == results[2]
