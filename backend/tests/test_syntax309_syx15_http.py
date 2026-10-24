"""Untrusted script text remains JSON error data, never a mathematical result."""
import os
import json
from pathlib import Path
os.environ.setdefault("CORS_ORIGINS","http://localhost:5173")
from fastapi.testclient import TestClient
from app.main import app

def test_syx15_original_script_text_rejection_and_http_recovery():
    row=next(json.loads(line) for line in (Path(__file__).resolve().parents[2]/"qa/certification/syntax309_cases.jsonl").read_text().splitlines() if json.loads(line)["id"]=="SY-X-15")
    assert row["entrada"]==r"\text{<script>alert(1)</script>}"
    assert row["esperado"]=="tratado como texto o error; **nunca** se ejecuta ni se inserta como HTML"
    ids=[]
    with TestClient(app) as client:
        r=client.post("/api/v1/evaluate",json={"expression":row["entrada"]})
        assert r.status_code==200,r.text
        assert r.headers["content-type"].startswith("application/json")
        b=r.json();assert not b["success"],b
        assert b["error_code"] in ["PARSE_ERROR","VALIDATION_ERROR"],b
        assert b["result_text"] is None and b["result_latex"] is None,b
        assert b["error_message"],b
        ids.append(b["request_id"])
        for source in ["2+3","5"]:
            r=client.post("/api/v1/evaluate",json={"expression":source})
            assert r.status_code==200
            b=r.json();assert b["success"] and b["result_text"]=="5",b
            ids.append(b["request_id"])
    assert len(set(ids))==3
