"""SY-V-24: original LaTeX absolute bars of complex numbers via HTTP."""
import json
import os
from pathlib import Path
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse
ROWS = {r["id"]: r for r in (json.loads(line) for line in
    (Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl")
    .read_text(encoding="utf-8").splitlines() if line.strip())}

def test_syv24_original_complex_modulus_and_http_reentry():
    row = ROWS["SY-V-24"]
    assert row["entrada"] == r"\lvert3+4i\rvert" and row["esperado"] == "5"
    assert row["operacion"] == "valor"
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": row["entrada"]})
        assert response.status_code == 200, response.text
        data = response.json()
        MathResponse.model_validate(data)
        assert data["success"] is True and data["result_text"] == "5", data
        assert data["result_approx"] == 5 and data["input_text"] == row["entrada"], data
        again = client.post("/api/v1/evaluate", json={"expression": data["result_text"]}).json()
        MathResponse.model_validate(again)
        assert again["success"] is True and again["result_text"] == "5", again
        assert again["request_id"] != data["request_id"], again

def test_syv24_complex_sign_controls():
    with TestClient(app) as client:
        for source, expected in [(r"\lvert3-4i\rvert", "5"), (r"\lvert-3+4i\rvert", "5"),
                                 (r"\lvert-3-4i\rvert", "5"), (r"\lvert5+12i\rvert", "13")]:
            result = client.post("/api/v1/evaluate", json={"expression": source}).json()
            MathResponse.model_validate(result)
            assert result["success"] is True and result["result_text"] == expected, result
