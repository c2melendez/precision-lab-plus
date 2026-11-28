"""Limited parity observation against frozen, independently verified PHUMA stimuli."""
import json
import os
from fractions import Fraction
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app

CASES=json.loads((Path(__file__).resolve().parents[2]/"qa/stem/arithmetic-pilot.json").read_text(encoding="utf-8"))["cases"]
client=TestClient(app)

@pytest.mark.parametrize("case",CASES,ids=[case["id"] for case in CASES])
def test_stem_rational_pilot(case):
    response=client.post("/api/v1/evaluate",json={"expression":case["expression"]})
    body=response.json()
    assert response.status_code == 200
    assert body["success"] is True, body
    assert Fraction(body["result_text"].replace(" ","")) == Fraction(case["expected"])
    assert body["result_approx"] == pytest.approx(float(Fraction(case["expected"])),rel=1e-12,abs=1e-12)
