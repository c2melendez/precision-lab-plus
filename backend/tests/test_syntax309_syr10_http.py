"""SY-R-10 exact rational identity, persistent domain exclusions and result_text reentry."""
import os
import pytest
import sympy as sp
from fastapi.testclient import TestClient
os.environ.setdefault("CORS_ORIGINS","http://localhost:5173")
from app.main import app
from app.schemas.responses import MathResponse

@pytest.mark.parametrize("source, expected, variable, pole", [
    ("((x+1)/(x-1))^2","(x+1)^2/(x-1)^2","x",1),
    ("(x+1)^2/(x-1)^2","(x+1)^2/(x-1)^2","x",1),
    ("((y+2)/(y-2))^2","(y+2)^2/(y-2)^2","y",2),
    ("((2*x+1)/(x-1))^2","(2*x+1)^2/(x-1)^2","x",1),
])
def test_syr10_exact_rational_domain_and_reentry(source, expected, variable, pole):
    symbol=sp.Symbol(variable)
    def check(result):
        assert result.success and result.result_type.value=="scalar" and result.result_latex, result
        actual=sp.sympify(result.result_text)
        assert not actual.has(sp.Float), result
        assert sp.cancel(actual-sp.sympify(expected))==0, result
        candidates=[sp.sympify(c.text) for c in result.domain_conditions if c.kind=="denominator" and c.variable==variable]
        assert any(c.subs(symbol,pole)==sp.false and c.subs(symbol,pole+1)==sp.true for c in candidates), result
    with TestClient(app) as client:
        response=client.post("/api/v1/evaluate",json={"expression":source})
        assert response.status_code==200,response.text
        result=MathResponse.model_validate(response.json())
        check(result)
        again=client.post("/api/v1/evaluate",json={"expression":result.result_text})
        assert again.status_code==200,again.text
        check(MathResponse.model_validate(again.json()))
        invalid=client.post("/api/v1/evaluate",json={"expression":result.result_text,"substitutions":{variable:str(pole)}})
        assert invalid.status_code==200,invalid.text
        rejected=MathResponse.model_validate(invalid.json())
        assert not rejected.success and rejected.error_code.value=="DOMAIN_ERROR",rejected
