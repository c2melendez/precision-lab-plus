"""SY-X-05: real30-level raw source, exact scalar, controls and HTTP reentry."""
import json
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
from app.main import app


def test_syx05_canonical_expansion():
    rows = (Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl").read_text().splitlines()
    row = next(json.loads(line) for line in rows if json.loads(line)["id"] == "SY-X-05")
    assert row["entrada"] == r"\underbrace{(\cdots((1))\cdots)}_{30\text{ niveles}}"
    assert row["esperado"] == "1"
    source = "(" * 30 + "1" + ")" * 30
    assert len(source) == 61 and source.count("(") == source.count(")") == 30


@pytest.mark.parametrize("inner,expected", [("1", "1"), ("7", "7"), ("2+3", "5")])
def test_syx05_raw_http_depth_and_reentry(inner, expected):
    source = "(" * 30 + inner + ")" * 30
    with TestClient(app) as client:
        ids = []
        body = None
        for index, result in enumerate([expected, expected, "5"]):
            expression = source if index == 0 else body["result_latex"] if index == 1 else "2+3"
            response = client.post("/api/v1/evaluate", json={"expression": expression})
            assert response.status_code == 200, response.text
            body = response.json()
            assert body["success"] and body["result_text"] == body["result_latex"] == result, body
            assert body["result_approx"] == int(result), body
            assert body["request_id"] and body["request_id"] not in ids
            ids.append(body["request_id"])
