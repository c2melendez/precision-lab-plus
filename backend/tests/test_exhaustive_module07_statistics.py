"""Suite exhaustiva original — Módulo 7: Estadística.

QA-only. No modifica código de producto.
"""
import math
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=False)

def post(path, payload):
    return client.post(f"/api/v1/{path}", json=payload)

def approx(body, expected, tol=1e-9):
    assert body["success"] is True, body
    assert body["result_approx"] == pytest.approx(expected, abs=tol), body

def test_m7_descriptive_known_values():
    vals = [1,2,3,4,5]
    for stat, expected in [
        ("mean",3),("median",3),("sum",15),("sumsq",55),("n",5),
        ("min",1),("max",5),("range",4),("q1",2),("q2",3),("q3",4),("iqr",2),
    ]:
        b = post("statistics/descriptive", {"values":vals,"stat":stat,"variance_kind":"population"}).json()
        approx(b, expected)

    p90 = post("statistics/descriptive", {
        "values":vals,"stat":"percentile","variance_kind":"population","percentile_p":90
    }).json()
    approx(p90, 4.6)

def test_m7_population_and_sample_variance_stdev():
    vals = [1,2,3,4,5]
    popvar = post("statistics/descriptive", {"values":vals,"stat":"variance","variance_kind":"population"}).json()
    samvar = post("statistics/descriptive", {"values":vals,"stat":"variance","variance_kind":"sample"}).json()
    popsd = post("statistics/descriptive", {"values":vals,"stat":"stdev","variance_kind":"population"}).json()
    samsd = post("statistics/descriptive", {"values":vals,"stat":"stdev","variance_kind":"sample"}).json()
    approx(popvar, 2)
    approx(samvar, 2.5)
    approx(popsd, math.sqrt(2))
    approx(samsd, math.sqrt(2.5))

def test_m7_mode_and_combinatorics():
    mode = post("statistics/descriptive", {
        "values":[1,1,2,3],"stat":"mode","variance_kind":"population"
    }).json()
    assert mode["success"] is True
    assert mode["result_text"] == "1"

    for payload, expected in [
        ({"n":5,"r":2,"fn":"nCr"}, 10),
        ({"n":5,"r":2,"fn":"nPr"}, 20),
        ({"n":5,"r":0,"fn":"factorial"}, 120),
    ]:
        approx(post("statistics/combinatorics", payload).json(), expected)

def test_m7_correlation_and_regression():
    x=[1,2,3,4]
    y=[3,5,7,9]
    approx(post("statistics/correlation", {"x":x,"y":y,"query":"correlation"}).json(), 1)
    approx(post("statistics/correlation", {"x":x,"y":y,"query":"slope"}).json(), 2)
    approx(post("statistics/correlation", {"x":x,"y":y,"query":"intercept"}).json(), 1)

def test_m7_binomial_and_normal():
    approx(post("statistics/binomial", {"n":4,"p":0.5,"k":2,"query":"pmf"}).json(), 0.375)
    approx(post("statistics/binomial", {"n":4,"p":0.5,"k":2,"query":"cdf"}).json(), 0.6875)
    approx(post("statistics/binomial", {"n":4,"p":0.5,"k":2,"query":"mean"}).json(), 2)
    approx(post("statistics/binomial", {"n":4,"p":0.5,"k":2,"query":"variance"}).json(), 1)
    approx(post("statistics/normal", {"mu":0,"sigma":1,"x":0,"a":-1,"b":1,"query":"cdf"}).json(), 0.5, 1e-12)
    approx(post("statistics/normal", {"mu":10,"sigma":2,"x":14,"a":0,"b":1,"query":"zscore"}).json(), 2)

def test_m7_poisson_uniform_exponential():
    approx(post("statistics/poisson", {"lam":4,"k":2,"query":"mean"}).json(), 4)
    approx(post("statistics/poisson", {"lam":4,"k":2,"query":"variance"}).json(), 4)
    approx(post("statistics/uniform", {"a":0,"b":10,"x":5,"query":"cdf"}).json(), 0.5)
    approx(post("statistics/uniform", {"a":0,"b":10,"x":5,"query":"mean"}).json(), 5)
    approx(post("statistics/uniform", {"a":0,"b":10,"x":5,"query":"variance"}).json(), 100/12)
    approx(post("statistics/exponential", {"lam":2,"x":1,"query":"mean"}).json(), 0.5)
    approx(post("statistics/exponential", {"lam":2,"x":1,"query":"variance"}).json(), 0.25)
    approx(post("statistics/exponential", {"lam":2,"x":0,"query":"cdf"}).json(), 0)

def test_m7_invalid_parameters_rejected():
    cases = [
        ("statistics/descriptive", {"values":[1,2,3],"stat":"percentile","variance_kind":"population","percentile_p":101}),
        ("statistics/correlation", {"x":[1,1,1],"y":[1,2,3],"query":"correlation"}),
        ("statistics/binomial", {"n":4,"p":1.5,"k":2,"query":"pmf"}),
        ("statistics/normal", {"mu":0,"sigma":0,"x":0,"a":-1,"b":1,"query":"cdf"}),
        ("statistics/poisson", {"lam":0,"k":2,"query":"pmf"}),
        ("statistics/uniform", {"a":2,"b":2,"x":2,"query":"cdf"}),
        ("statistics/exponential", {"lam":0,"x":1,"query":"cdf"}),
    ]
    for path,payload in cases:
        b = post(path,payload).json()
        assert b["success"] is False, (path,b)
        assert b["error_code"] == "DOMAIN_ERROR", (path,b)
