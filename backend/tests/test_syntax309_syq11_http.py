"""SY-Q-11: official 2x2 linear system via real Plus HTTP routing."""
import json
import os
from pathlib import Path

from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse

_ROWS = {row["id"]: row for row in (json.loads(line) for line in
    (Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl")
    .read_text(encoding="utf-8").splitlines() if line.strip())}

def test_syq11_public_system_unique_ordered_solution():
    row = _ROWS["SY-Q-11"]
    assert row["entrada"] == r"\begin{cases}x+y=3\\ x-y=1\end{cases}"
    assert row["esperado"] == "(x,y)=(2,1)"
    with TestClient(app) as client:
        first = client.post("/api/v1/solve/system", json={
            "equations": ["x+y=3", "x-y=1"], "variables": ["x", "y"]
        })
        assert first.status_code == 200, first.text
        result = MathResponse.model_validate(first.json())
        assert result.success is True
        assert result.operation.value == "solve_system"
        assert result.result_data is not None
        assert len(result.result_data) == 1, first.text
        assert result.result_data[0].text.replace(" ", "") == "x=2,y=1"
        assert result.result_data[0].is_complex is False
        assert result.request_id
        swapped = client.post("/api/v1/solve/system", json={
            "equations": ["x-y=1", "x+y=3"], "variables": ["x", "y"]
        })
        assert swapped.status_code == 200, swapped.text
        again = MathResponse.model_validate(swapped.json())
        assert again.success and again.result_data[0].text == result.result_data[0].text
        assert again.request_id != result.request_id
