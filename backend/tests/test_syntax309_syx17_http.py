"""Reject original shell escape; never invoke its command, even in controls."""
import os
import sys
import json
from contextlib import contextmanager
from pathlib import Path
os.environ.setdefault("CORS_ORIGINS","http://localhost:5173")
import pytest
from fastapi.testclient import TestClient
from app.main import app

LAUNCH_EVENTS=("subprocess.Popen","os.system","os.posix_spawn","os.exec","os.spawn","os.fork","pty.spawn")
@contextmanager
def forbid_process_launch():
    attempts=[]
    active=[True]
    def audit(event,args):
        if active[0] and event in LAUNCH_EVENTS:
            attempts.append(event)
            raise PermissionError("SY-X-17 test guard: process launch forbidden")
    sys.addaudithook(audit)
    try:
        yield attempts
    finally:
        active[0]=False

@pytest.mark.parametrize("event",LAUNCH_EVENTS)
def test_syx17_guard_detects_synthetic_launch_events_without_process(event):
    with forbid_process_launch() as attempts:
        # Only notifies hooks; no subprocess/system/spawn/exec/fork API is called.
        with pytest.raises(PermissionError,match="process launch forbidden"):
            sys.audit(event,"__syntax17_nonexistent_control__")
        assert attempts==[event]

def test_syx17_original_shell_http_rejects_without_process_launch_and_recovers():
    row=next(json.loads(line) for line in (Path(__file__).resolve().parents[2]/"qa/certification/syntax309_cases.jsonl").read_text().splitlines() if json.loads(line)["id"]=="SY-X-17")
    assert row["entrada"]==r"\write18{ls}"
    assert row["esperado"]=="ignorado o rechazado; sin ejecución"
    ids=[]
    with TestClient(app) as client,forbid_process_launch() as attempts:
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
        assert attempts==[] # a caught/blocked launch attempt is still a test failure
    assert len(set(ids))==3
