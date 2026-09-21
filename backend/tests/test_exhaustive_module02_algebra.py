"""Suite exhaustiva original — Módulo 2: Álgebra.

QA-only. No modifica código de producto.
Cubre logs, exponenciales, radicales, álgebra general, ecuaciones,
sistemas hasta 5x5 e inecuaciones de una variable.
"""

import math
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=False)

def post(path, payload):
    return client.post(f"/api/v1/{path}", json=payload)

@pytest.mark.parametrize(
    "expression,expected",
    [
        ("log(100)", 2.0),
        ("log(8,2)", 3.0),
        ("ln(e)", 1.0),
        ("exp(1)", math.e),
        ("10**3", 1000.0),
        ("sqrt(81)", 9.0),
        ("sqrt(2)**2", 2.0),
    ],
)
def test_module02_known_numeric_values(expression, expected):
    r = post("evaluate", {"expression": expression, "angle_unit": "rad"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["success"] is True, body
    assert body["result_approx"] == pytest.approx(expected, abs=1e-10)

def test_module02_simplify_factor_expand():
    cases = [
        ("simplify", {"expression": "(x**2-1)/(x-1)"}, "x + 1"),
        ("factor", {"expression": "x**2-5*x+6"}, None),
        ("expand", {"expression": "(x+2)**3"}, None),
    ]
    for path, payload, exact in cases:
        r = post(path, payload)
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["success"] is True, body
        if exact is not None:
            assert body["result_text"] == exact

def test_module02_equations_known_and_edges():
    r = post("solve", {"equation": "x**2-5*x+6=0", "variable": "x", "angle_unit": "rad"})
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert {x["text"] for x in body["result_data"]} == {"2", "3"}

    identity = post("solve", {"equation": "2=2", "angle_unit": "rad"}).json()
    contradiction = post("solve", {"equation": "2=3", "angle_unit": "rad"}).json()
    assert identity["success"] is True and identity["result_type"] == "identity"
    assert contradiction["success"] is True and contradiction["result_type"] == "contradiction"

    ambiguous = post("solve", {"equation": "x+y=0", "angle_unit": "rad"}).json()
    assert ambiguous["success"] is False
    assert ambiguous["error_code"] == "AMBIGUOUS_VARIABLE"

def test_module02_systems_up_to_5x5():
    unique = post("solve/system", {
        "equations": ["x1=1", "x2=2", "x3=3", "x4=4", "x5=5"],
        "variables": ["x1", "x2", "x3", "x4", "x5"],
    })
    assert unique.status_code == 200
    body = unique.json()
    assert body["success"] is True
    text = " ".join(item["text"] for item in body["result_data"])
    for expected in ["x1=1", "x2=2", "x3=3", "x4=4", "x5=5"]:
        assert expected in text

    infinite = post("solve/system", {
        "equations": ["x+y=2", "2*x+2*y=4"],
        "variables": ["x", "y"],
    }).json()
    assert infinite["success"] is True
    assert infinite["result_data"]
    assert any("y=y" in item["text"].replace(" ", "") for item in infinite["result_data"])

    inconsistent = post("solve/system", {
        "equations": ["x+y=1", "x+y=2"],
        "variables": ["x", "y"],
    }).json()
    assert inconsistent["success"] is True
    assert inconsistent["result_data"] == []
    assert any("no tiene solución" in w.lower() for w in inconsistent["warnings"])

def test_module02_one_variable_inequalities():
    cases = [
        ("2*x+1<7", "Interval.open(-oo, 3)"),
        ("x**2<4", "Interval.open(-2, 2)"),
        ("x**2<0", "EmptySet"),
    ]
    for inequality, expected in cases:
        r = post("inequality", {"inequality": inequality, "variable": "x"})
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["success"] is True, body
        assert body["result_text"] == expected

def test_module02_rejections_are_explicit():
    bad_log = post("evaluate", {"expression": "log(8,2,3)", "angle_unit": "rad"}).json()
    assert bad_log["success"] is False
    assert bad_log["error_code"] == "PARSE_ERROR"

    multivar_ineq = post("inequality", {"inequality": "x+y<5"}).json()
    assert multivar_ineq["success"] is False
    assert multivar_ineq["error_code"] == "VALIDATION_ERROR"
