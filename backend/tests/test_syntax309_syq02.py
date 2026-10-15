"""SY-Q-02: standard-form quadratic roots using actual HTTP solve."""
import json
import os
from pathlib import Path
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
ROWS = {r["id"]: r for r in (json.loads(line) for line in
    (Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl")
    .read_text(encoding="utf-8").splitlines() if line.strip())}

def test_syq02_quadratic_standard_form_and_equivalence():
    row = ROWS["SY-Q-02"]
    assert row["entrada"] == "x^{2}-4=0" and row["operacion"] == "resolver"
    with TestClient(app) as client:
        results = []
        for equation in ("x^2-4=0", "x^2=4"):
            response = client.post("/api/v1/solve", json={"equation": equation, "variable": "x"})
            assert response.status_code == 200, response.text
            data = response.json()
            assert data["success"] is True, data
            roots = sorted(float(s["text"]) for s in data["result_data"])
            assert roots == [-2.0, 2.0], data
            assert all(r*r-4 == 0 for r in roots)
            results.append(roots)
        assert results[0] == results[1]
