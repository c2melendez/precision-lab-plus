"""SY-Q-19 public HTTP rejects chained equality and recovers."""
import json
import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS","http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse

ROWS={r["id"]:r for r in (json.loads(s) for s in
    (Path(__file__).resolve().parents[2]/"qa/certification/syntax309_cases.jsonl")
    .read_text(encoding="utf-8").splitlines() if s.strip())}

def test_syq19_original_fixture_and_recovery():
    row=ROWS["SY-Q-19"]
    assert row["entrada"]=="x=y=3" and row["operacion"]=="error"
    assert "igualdad encadenada" in row["esperado"]
    with TestClient(app) as client:
        response=client.post("/api/v1/solve",json={"equation":row["entrada"],"variable":"x"})
        assert response.status_code==200,response.text
        result=MathResponse.model_validate(response.json())
        assert not result.success,response.text
        assert result.operation.value=="solve"
        assert result.error_code.value=="PARSE_ERROR"
        assert "=" in result.error_message
        assert result.result_data is None and result.result_latex is None
        assert not result.has_detailed_steps
        recovered=client.post("/api/v1/solve",json={"equation":"x+1=4","variable":"x"})
        answer=MathResponse.model_validate(recovered.json())
        assert answer.success,recovered.text
        assert len(answer.result_data)==1 and answer.result_data[0].text=="3"
        assert result.request_id!=answer.request_id

@pytest.mark.parametrize("equation",["x=y=3","y=x=3","x = y = 3","x=3=3","x==3","x=(y=3)","f(x)=x=3"])
@pytest.mark.parametrize("variable",[None,"x","y"])
def test_syq19_rejection_does_not_depend_on_variable(equation,variable):
    payload={"equation":equation}
    if variable is not None: payload["variable"]=variable
    with TestClient(app) as client:
        response=client.post("/api/v1/solve",json=payload)
        result=MathResponse.model_validate(response.json())
        assert response.status_code==200,response.text
        assert not result.success and result.error_code.value=="PARSE_ERROR",response.text
        assert result.error_message and result.result_data is None

def test_syq19_separate_equations_are_a_system_not_a_chain():
    with TestClient(app) as client:
        response=client.post("/api/v1/solve/system",json={"equations":["x=y","y=3"],"variables":["x","y"]})
        result=MathResponse.model_validate(response.json())
        assert result.success,response.text
        assert len(result.result_data)==1
        assert result.result_data[0].text.replace(" ","")=="x=3,y=3"
