"""SY-Q-18 /solve: explicit variable, symbolic free parameter and reentry."""
import json
import os
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS","http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse

ROWS={r["id"]:r for r in (json.loads(s) for s in
    (Path(__file__).resolve().parents[2]/"qa/certification/syntax309_cases.jsonl")
    .read_text(encoding="utf-8").splitlines() if s.strip())}

def test_syq18_explicit_x_free_y_and_reentry():
    row=ROWS["SY-Q-18"]
    assert row["entrada"]=="x+y=3"
    assert "x=3-y" in row["esperado"] and "libre" in row["esperado"]
    x,y=sp.symbols("x y")
    with TestClient(app) as client:
        response=client.post("/api/v1/solve",json={"equation":row["entrada"],"variable":"x"})
        assert response.status_code==200,response.text
        result=MathResponse.model_validate(response.json())
        assert result.success,response.text
        assert result.operation.value=="solve"
        assert result.result_type.value=="equation_solutions"
        assert result.input_text==row["entrada"]
        assert len(result.result_data)==1
        value=sp.sympify(result.result_data[0].text)
        assert value.free_symbols=={y}
        assert sp.simplify(value+y-3)==0
        assert "Se despeja x; parámetros libres: y." in result.warnings
        for parameter in [-5,0,1,3,9]:
            assert value.subs(y,parameter)+parameter==3
        actual_equation="x="+result.result_data[0].text
        replay_response=client.post("/api/v1/solve",json={"equation":actual_equation,"variable":"x"})
        replay=MathResponse.model_validate(replay_response.json())
        assert replay.success,replay_response.text
        assert replay.request_id!=result.request_id
        assert sp.simplify(sp.sympify(replay.result_data[0].text)-value)==0

def test_syq18_does_not_select_variable_silently():
    with TestClient(app) as client:
        response=client.post("/api/v1/solve",json={"equation":"x+y=3"})
        result=MathResponse.model_validate(response.json())
        assert not result.success,response.text
        assert result.error_code.value=="AMBIGUOUS_VARIABLE"

def test_syq18_explicit_y_and_scaled_controls():
    with TestClient(app) as client:
        for equation,variable,expected,parameter in [
            ("x+y=3","y","3-x","x"),
            ("2*x+2*y=6","x","3-y","y"),
            ("2*x+y=3","x","(3-y)/2","y"),
        ]:
            response=client.post("/api/v1/solve",json={"equation":equation,"variable":variable})
            result=MathResponse.model_validate(response.json())
            assert result.success,response.text
            assert len(result.result_data)==1
            assert sp.simplify(sp.sympify(result.result_data[0].text)-sp.sympify(expected))==0
            assert f"Se despeja {variable}; parámetros libres: {parameter}." in result.warnings
