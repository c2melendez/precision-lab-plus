"""Evidence of SY-X-04's HTTP contract blocker, not a PASS of its 500x oracle."""
import json
import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse


def test_syx04_original_expansion_is_blocked_by_existing_http_contract_and_recovers():
    rows = (Path(__file__).resolve().parents[2] / "qa" / "certification" / "syntax309_cases.jsonl").read_text().splitlines()
    row = next(json.loads(line) for line in rows if json.loads(line)["id"] == "SY-X-04")
    assert row["entrada"] == r"x+x+x+\cdots+x\ \text{(500 términos)}"
    assert row["esperado"] == "500x"
    source = "+".join(["x"] * 500)
    assert len(source) == 999
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": source})
        assert response.status_code == 422, response.text
        rejected = MathResponse.model_validate(response.json())
        assert not rejected.success and rejected.error_code.value == "VALIDATION_ERROR"
        assert rejected.result_text is None and rejected.result_latex is None
        recovered = client.post("/api/v1/evaluate", json={"expression": "2+3"})
        assert recovered.status_code == 200
        result = MathResponse.model_validate(recovered.json())
        assert result.success and result.result_text == "5"
        assert result.request_id != rejected.request_id


@pytest.mark.parametrize("terms,status,error", [
    (199,200,None),
    (200,200,"COMPLEXITY_LIMIT"),
    (250,200,"COMPLEXITY_LIMIT"),
    (251,422,"VALIDATION_ERROR"),
])
def test_length_and_ast_boundaries_without_replacing_the_expanded_source(terms, status, error):
    source = "+".join(["x"] * terms)
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": source})
        assert response.status_code == status, response.text
        result = MathResponse.model_validate(response.json())
        if error is None:
            assert result.success and result.result_text == "199*x"
        else:
            assert not result.success and result.error_code.value == error
            assert result.result_text is None and result.result_latex is None
