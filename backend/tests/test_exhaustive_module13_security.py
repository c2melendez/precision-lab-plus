"""Suite exhaustiva original — Módulo 13: Seguridad.

QA-only. No modifica código de producto.
Verifica ast_validator, rechazo por dominio y seguridad específica de EDO.
"""

import sympy
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.ast_validator import validate_ast_safety
from app.services.parsing import ParseSecurityError

client = TestClient(app, raise_server_exceptions=False)


def test_m13_ast_validator_blocks_required_sympy_nodes_directly():
    x = sympy.Symbol("x")
    i = sympy.Symbol("i")
    blocked = [
        sympy.Derivative(x**2, x, evaluate=False),
        sympy.Integral(x, x),
        sympy.Sum(i, (i, 1, 5)),
        sympy.Product(i, (i, 1, 5)),
        sympy.Limit(sympy.sin(x) / x, x, 0),
        sympy.Lambda(x, x + 1),
        sympy.Matrix([[1, 2], [3, 4]]),
        sympy.Function("evil")(x),
    ]
    for tree in blocked:
        with pytest.raises(ParseSecurityError):
            validate_ast_safety(tree)


@pytest.mark.parametrize(
    "expression",
    [
        "Derivative(x**2,x)",
        "Integral(x,x)",
        "Sum(i,(i,1,5))",
        "Product(i,(i,1,5))",
        "Limit(sin(x)/x,x,0)",
        "Lambda(x,x+1)",
        "Matrix([[1,2],[3,4]])",
    ],
)
def test_m13_general_evaluate_blocks_forbidden_constructs(expression):
    r = client.post("/api/v1/evaluate", json={"expression": expression, "angle_unit": "rad"})
    b = r.json()
    assert r.status_code == 200, b
    assert b["success"] is False, (expression, b)
    assert b["error_code"] == "PARSE_ERROR", (expression, b)


@pytest.mark.parametrize(
    "label,path,payload",
    [
        ("algebra", "/api/v1/simplify", {"expression": "eval(1)"}),
        ("derivative", "/api/v1/derivative", {"expression": "eval(1)", "variable": "x", "order": 1}),
        ("integral", "/api/v1/integral", {"expression": "eval(1)", "variable": "x"}),
        ("graph", "/api/v1/graph/2d", {"expressions": ["eval(1)"], "variable": "x"}),
        ("matrix", "/api/v1/matrix/determinant", {"matrix": [["eval(1)", "0"], ["0", "1"]]}),
        ("complex", "/api/v1/complex/residue", {"expression": "eval(1)", "point": "z=0"}),
    ],
)
def test_m13_out_of_whitelist_is_controlled_per_domain(label, path, payload):
    r = client.post(path, json=payload)
    b = r.json()
    assert r.status_code == 200, (label, b)
    assert b["success"] is False, (label, b)
    assert b["error_code"] == "PARSE_ERROR", (label, b)
    assert "traceback" not in (b.get("error_message") or "").lower()


@pytest.mark.parametrize("expression", ["foo(x)", "dsolve(x)"])
def test_m13_general_evaluate_does_not_turn_unknown_functions_into_multiplication(expression):
    r = client.post("/api/v1/evaluate", json={"expression": expression, "angle_unit": "rad"})
    b = r.json()
    assert r.status_code == 200, b
    assert b["success"] is False, (expression, b)
    assert b["error_code"] == "PARSE_ERROR", (expression, b)


@pytest.mark.parametrize(
    "expression",
    [
        "y'=foo(x)",
        "y'=__import__('os')",
        "y'=x.__class__",
        "y'=Lambda(x,x)",
    ],
)
def test_m13_ode_out_of_whitelist_never_returns_500_or_raw_engine_error(expression):
    r = client.post("/api/v1/ode", json={"expression": expression})
    b = r.json()
    assert r.status_code == 200, (expression, r.status_code, b)
    assert b["success"] is False, (expression, b)
    assert b["error_code"] in {"PARSE_ERROR", "UNSUPPORTED_OPERATION"}, (expression, b)
    msg = (b.get("error_message") or "").lower()
    for forbidden in ["traceback", "sympifyerror", "tokenerror", "typeerror"]:
        assert forbidden not in msg, (expression, b)
