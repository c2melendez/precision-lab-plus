"""Actual HTTP derivative and output reentry, positive-real oracle scope."""
import os
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.responses import MathResponse

def test_syx13_http_exact_derivative_reentry_and_recovery():
    x=sp.Symbol("x",positive=True)
    expected=x**(x**x)*(x**x*(sp.log(x)+1)*sp.log(x)+x**(x-1))
    ids=[]
    with TestClient(app) as client:
        response=client.post("/api/v1/derivative",json={"expression":"x**(x**x)","variable":"x","order":1})
        for iteration in range(2):
            assert response.status_code==200,response.text
            body=response.json()
            MathResponse.model_validate(body)
            assert body["success"] and body["result_latex"],body
            assert body["error_code"] is None,body
            actual=sp.sympify(body["result_text"],locals={"x":x})
            assert not actual.has(sp.Derivative),body
            assert sp.simplify(actual-expected)==0,body
            ids.append(body["request_id"])
            if iteration==0:
                # SymPy machine text uses log=ln; calculator input log is base10.
                # Native UI reentry separately consumes the actual ln LaTeX.
                assert r"\ln" in body["result_latex"],body
                response=client.post("/api/v1/evaluate",json={"expression":body["result_text"].replace("log(","ln(")})
        for source in ["2+3","5"]:
            response=client.post("/api/v1/evaluate",json={"expression":source})
            assert response.status_code==200,response.text
            body=response.json()
            assert body["success"] and body["result_text"]=="5",body
            ids.append(body["request_id"])
    assert len(set(ids))==4
