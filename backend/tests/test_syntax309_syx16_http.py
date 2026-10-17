"""Original input command must not open its target. Audit guard never reads it."""
import os
import sys
import json
from pathlib import Path
os.environ.setdefault("CORS_ORIGINS","http://localhost:5173")
import pytest
from fastapi.testclient import TestClient
from app.main import app

from tests.file_access_probe import forbid_target_read

def test_syx16_audit_guard_detects_synthetic_open_event_without_file_access():
    with forbid_target_read() as attempts:
        # Emits only an audit event. Does not invoke open or read any file.
        with pytest.raises(PermissionError,match="target access forbidden"):
            sys.audit("open","/etc/passwd","r",0)
        assert attempts==["/etc/passwd"]

def test_syx16_original_input_http_rejects_without_open_and_recovers():
    row=next(json.loads(line) for line in (Path(__file__).resolve().parents[2]/"qa/certification/syntax309_cases.jsonl").read_text().splitlines() if json.loads(line)["id"]=="SY-X-16")
    assert row["entrada"]==r"\input{/etc/passwd}"
    assert row["esperado"]=="ignorado o rechazado; sin lectura de archivos"
    ids=[]
    with TestClient(app) as client,forbid_target_read() as attempts:
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
        assert attempts==[] # a caught/blocked read attempt is still a test failure
    assert len(set(ids))==3
