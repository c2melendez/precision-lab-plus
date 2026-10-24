"""Original50 reciprocal layers exceed existing depth30; never fake parity PASS."""
import json
import os
from pathlib import Path
os.environ.setdefault("CORS_ORIGINS","http://localhost:5173")
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.evaluate_service import evaluate
from app.services.ast_validator import ComplexityLimitError

def nested(depth,inner="x"):
    for _ in range(depth):inner="1/("+inner+")"
    return inner

def test_syx14_canonical_expansion_and_depth_limit_http_recovery():
    rows=[json.loads(line) for line in (Path(__file__).resolve().parents[2]/"qa/certification/syntax309_cases.jsonl").read_text().splitlines()]
    row=next(r for r in rows if r["id"]=="SY-X-14")
    assert row["entrada"]==r"\underbrace{\frac{1}{\frac{1}{\cdots\frac{1}{x}}}}_{50\text{ niveles}}"
    assert row["esperado"]==r"`x` o `\frac{1}{x}` según la paridad de los niveles (50 → `x`)"
    source=nested(50)
    assert len(source)==201 and source.count("/")==50
    ids=[]
    with TestClient(app) as client:
        r=client.post("/api/v1/evaluate",json={"expression":source})
        assert r.status_code==200,r.text
        b=r.json()
        assert not b["success"] and b["error_code"]=="COMPLEXITY_LIMIT",b
        assert "profundidad máxima de 30" in b["error_message"],b
        assert b["result_latex"] is None and b["result_text"] is None,b
        ids.append(b["request_id"])
        for source in ["2+3","5"]:
            r=client.post("/api/v1/evaluate",json={"expression":source})
            assert r.status_code==200
            b=r.json();assert b["success"] and b["result_text"]=="5",b
            ids.append(b["request_id"])
    assert len(set(ids))==3

@pytest.mark.xfail(strict=True,raises=ComplexityLimitError,reason="SY-X-14 BLOCKED:50 original reciprocal layers exceed existing AST depth30; preserve parity oracle x with x!=0")
def test_syx14_original50_mathematical_oracle_not_bypassed():
    import sympy as sp
    result=evaluate(nested(50),"rad",None)
    assert sp.simplify(result.expr-sp.Symbol("x"))==0
