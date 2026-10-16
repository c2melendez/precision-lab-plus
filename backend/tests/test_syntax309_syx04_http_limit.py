"""SY-X-04: explicit 500-addend expression exceeds the existing 500-character HTTP limit.

The 422 is evidence of a contract boundary, NOT a mathematical PASS of SY-X-04.
"""
from fastapi.testclient import TestClient
from app.main import app


def test_syx04_500_explicit_addends_are_rejected_and_endpoint_recovers():
    source = "+".join(["x"] * 500)
    assert len(source) == 999
    assert source.count("x") == 500

    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": source})
        assert response.status_code == 422
        rejected = response.json()
        assert rejected["success"] is False
        assert rejected["operation"] == "evaluate"
        assert rejected["error_code"] == "VALIDATION_ERROR"
        assert rejected["result_text"] is None
        assert rejected["result_latex"] is None
        assert rejected["request_id"]

        recovery = client.post("/api/v1/evaluate", json={"expression": "2+3"})
        assert recovery.status_code == 200
        accepted = recovery.json()
        assert accepted["success"] is True
        assert accepted["operation"] == "evaluate"
        assert accepted["result_text"] == "5"
        assert accepted["request_id"] != rejected["request_id"]
        assert not accepted["error_code"]
