"""SY-X-12: bounded, unmocked SymPy + HTTP integration of the original integrand."""
import json
import subprocess
import sys
from pathlib import Path

def test_syx12_real_http_is_non_fabricating_and_recovers():
    case = next(json.loads(line) for line in (
        Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl"
    ).read_text().splitlines() if json.loads(line)["id"] == "SY-X-12")
    assert case["entrada"] == r"\int\sin\left(x^{x}\right)dx"
    assert case["esperado"] == "sin forma elemental: aviso claro; no una antiderivada inventada"
    code = '''
import os
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
import json
from fastapi.testclient import TestClient
from app.main import app
with TestClient(app) as client:
    r=client.post("/api/v1/integral",json={"expression":"sin(x**x)","variable":"x"})
    assert r.status_code==200, r.text
    data=r.json()
    assert data["success"] is False, data
    assert data["error_code"]=="UNSUPPORTED_OPERATION", data
    assert data["result_text"] is None and data["result_latex"] is None, data
    assert "Sin forma elemental" in data["error_message"], data
    finite=client.post("/api/v1/integral",json={"expression":"x","variable":"x"})
    assert finite.status_code==200 and finite.json()["success"] is True, finite.text
print(json.dumps({"error_code":data["error_code"],"recovered":True}))
'''
    result = subprocess.run(
        [sys.executable, "-c", code], text=True, capture_output=True,
        timeout=20, check=False,
    )
    assert result.returncode == 0, f"stdout={result.stdout}\nstderr={result.stderr}"
