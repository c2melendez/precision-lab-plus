"""EDCX Parte A · A4 "Transformada de Laplace y ecuaciones integrales" (24 filas).

Canal
-----
El producto no expone ninguna operación de transformada de Laplace ni inversa:
`/api/v1/evaluate` rechaza `laplace` e `ilaplace` como funciones no reconocidas,
y el motor de EDO solo resuelve EDO escalares `y(x)`. Por eso 23 de las 24 filas
se miden como BLOCKED; ninguna se cuenta como PASS.

`ED-T-17` sí es una EDO de primer orden con una condición inicial. La fuente la
escribe en `t`; el motor solo habla `y(x)`, así que se ejecuta con el renombrado
`t -> x` (documentado) y se verifica simbólicamente contra la EDO y la condición
inicial, no contra el texto "Resultado esperado".

Bloqueos medidos
----------------
- ED-T-01..09: transformada directa; `laplace` no existe (PARSE_ERROR).
- ED-T-10..15: transformada inversa; `ilaplace` no existe (PARSE_ERROR).
- ED-T-16: es una convolución `t * e^t`, no una transformada. `integrate` no
  existe; además `/evaluate` sobre `t*exp(t)` devuelve el producto literal, sin
  semántica de convolución.
- ED-T-18..21: EDO de segundo orden con DOS condiciones iniciales. El canal
  acepta una sola: con coma responde "No se esperaba más de una condición
  inicial". La segunda condición separada por `;` que promete el docstring de
  `_parse_initial_condition` NO está implementada: llega al parser de valores y
  falla con "No se pudo interpretar la condición inicial" (defecto de producto
  medido, no corregido aquí).
- ED-T-20..21: además usan `dirac` / `heaviside`, funciones no permitidas.
- ED-T-22..23: ecuaciones integrales. El separador de comas corta la integral
  antes de parsear; y `integrate` tampoco existe en `/evaluate`.
- ED-T-24: sistema de EDOs; el canal escalar lo rechaza.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import pytest
import sympy
from fastapi.testclient import TestClient

from app.main import app
from app.services import ode_service

ROOT = Path(__file__).resolve().parents[2]
SOURCE_GZ = ROOT / "qa/certification/legacy_sources/matriz_edo_variable_compleja.md.gz"
JSONL = ROOT / "qa/certification/edcx_ejecutables.jsonl"

ROWS = [json.loads(line) for line in JSONL.read_text(encoding="utf-8").splitlines() if line.strip()]
A4 = [row for row in ROWS if row["bloque"] == "A4"]

X = sympy.Symbol("x")
Y = sympy.Function("y")

# Entrada normalizada al canal real (LaTeX de la fuente -> sintaxis del motor).
BACKEND_INPUT = {
    "ED-T-01": "laplace(t^n)",
    "ED-T-02": "laplace(exp(a*t))",
    "ED-T-03": "laplace(sin(b*t))",
    "ED-T-04": "laplace(exp(a*t)*sin(b*t))",
    "ED-T-05": "laplace(t*sin(t))",
    "ED-T-06": "laplace(heaviside(t-a))",
    "ED-T-07": "laplace(dirac(t-a))",
    "ED-T-08": "laplace(sin(t)/t)",
    "ED-T-09": "laplace(1/sqrt(t))",
    "ED-T-10": "ilaplace(1/(s*(s+1)))",
    "ED-T-11": "ilaplace(1/(s^2+2*s+5))",
    "ED-T-12": "ilaplace(1/(s^2*(s^2+1)))",
    "ED-T-13": "ilaplace(1/(s^2+1)^2)",
    "ED-T-14": "ilaplace(exp(-2*s)/s^2)",
    "ED-T-15": "ilaplace(1/((s-1)*(s-2)*(s-3)))",
    "ED-T-16": "integrate(tau*exp(t-tau),tau,0,t)",
    "ED-T-17": "y'+2*y=exp(-x), y(0)=1",
    "ED-T-18": "y''-y=exp(x), y(0)=0, y'(0)=0",
    "ED-T-19": "y''+2*y'+y=x*exp(-x), y(0)=0, y'(0)=0",
    "ED-T-20": "y''+y=dirac(x-pi), y(0)=0, y'(0)=0",
    "ED-T-21": "y''+4*y=heaviside(x-1), y(0)=0, y'(0)=0",
    "ED-T-22": "y'(t)=1-integrate(y(tau),tau,0,t), y(0)=0",
    "ED-T-23": "y(t)=t+integrate(sin(t-tau)*y(tau),tau,0,t)",
    "ED-T-24": "x'=y, y'=-x, x(0)=1, y(0)=0",
}

PASS_RENAMED = {"ED-T-17"}

# id -> variantes medidas (ruta, expresión, código, fragmento del mensaje).
BLOCKED = {
    "ED-T-01": [("/api/v1/evaluate", BACKEND_INPUT["ED-T-01"], "PARSE_ERROR", "laplace")],
    "ED-T-02": [("/api/v1/evaluate", BACKEND_INPUT["ED-T-02"], "PARSE_ERROR", "laplace")],
    "ED-T-03": [("/api/v1/evaluate", BACKEND_INPUT["ED-T-03"], "PARSE_ERROR", "laplace")],
    "ED-T-04": [("/api/v1/evaluate", BACKEND_INPUT["ED-T-04"], "PARSE_ERROR", "laplace")],
    "ED-T-05": [("/api/v1/evaluate", BACKEND_INPUT["ED-T-05"], "PARSE_ERROR", "laplace")],
    "ED-T-06": [("/api/v1/evaluate", BACKEND_INPUT["ED-T-06"], "PARSE_ERROR", "laplace")],
    "ED-T-07": [("/api/v1/evaluate", BACKEND_INPUT["ED-T-07"], "PARSE_ERROR", "laplace")],
    "ED-T-08": [("/api/v1/evaluate", BACKEND_INPUT["ED-T-08"], "PARSE_ERROR", "laplace")],
    "ED-T-09": [("/api/v1/evaluate", BACKEND_INPUT["ED-T-09"], "PARSE_ERROR", "laplace")],
    "ED-T-10": [("/api/v1/evaluate", BACKEND_INPUT["ED-T-10"], "PARSE_ERROR", "ilaplace")],
    "ED-T-11": [("/api/v1/evaluate", BACKEND_INPUT["ED-T-11"], "PARSE_ERROR", "ilaplace")],
    "ED-T-12": [("/api/v1/evaluate", BACKEND_INPUT["ED-T-12"], "PARSE_ERROR", "ilaplace")],
    "ED-T-13": [("/api/v1/evaluate", BACKEND_INPUT["ED-T-13"], "PARSE_ERROR", "ilaplace")],
    "ED-T-14": [("/api/v1/evaluate", BACKEND_INPUT["ED-T-14"], "PARSE_ERROR", "ilaplace")],
    "ED-T-15": [("/api/v1/evaluate", BACKEND_INPUT["ED-T-15"], "PARSE_ERROR", "ilaplace")],
    "ED-T-16": [("/api/v1/evaluate", BACKEND_INPUT["ED-T-16"], "PARSE_ERROR", "integrate")],
    "ED-T-18": [
        ("/api/v1/ode", BACKEND_INPUT["ED-T-18"], "PARSE_ERROR", "No se esperaba"),
        ("/api/v1/ode", "y''-y=exp(x), y(0)=0; y'(0)=0", "PARSE_ERROR", "No se pudo interpretar"),
    ],
    "ED-T-19": [
        ("/api/v1/ode", BACKEND_INPUT["ED-T-19"], "PARSE_ERROR", "No se esperaba"),
        ("/api/v1/ode", "y''+2*y'+y=x*exp(-x), y(0)=0; y'(0)=0", "PARSE_ERROR", "No se pudo interpretar"),
    ],
    "ED-T-20": [
        ("/api/v1/ode", "y''+y=dirac(x-pi), y(0)=0", "PARSE_ERROR", "dirac"),
        ("/api/v1/ode", BACKEND_INPUT["ED-T-20"], "PARSE_ERROR", "No se esperaba"),
    ],
    "ED-T-21": [
        ("/api/v1/ode", "y''+4*y=heaviside(x-1), y(0)=0", "PARSE_ERROR", "heaviside"),
        ("/api/v1/ode", BACKEND_INPUT["ED-T-21"], "PARSE_ERROR", "No se esperaba"),
    ],
    "ED-T-22": [
        ("/api/v1/ode", BACKEND_INPUT["ED-T-22"], "PARSE_ERROR", "No se esperaba"),
        ("/api/v1/evaluate", "integrate(tau,tau,0,t)", "PARSE_ERROR", "integrate"),
    ],
    "ED-T-23": [
        ("/api/v1/ode", BACKEND_INPUT["ED-T-23"], "PARSE_ERROR", "No se esperaba"),
        ("/api/v1/evaluate", "integrate(tau,tau,0,t)", "PARSE_ERROR", "integrate"),
    ],
    "ED-T-24": [("/api/v1/ode", BACKEND_INPUT["ED-T-24"], "PARSE_ERROR", "No se esperaba")],
}


def frozen_source() -> str:
    import gzip

    return gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")


def test_edcx_fixture_a4_matches_the_frozen_source():
    assert len(ROWS) == 638
    assert len(A4) == 24
    assert set(BACKEND_INPUT) == {row["id"] for row in A4}
    assert PASS_RENAMED == {"ED-T-17"}
    assert set(BLOCKED) | PASS_RENAMED == set(BACKEND_INPUT)
    assert not (set(BLOCKED) & PASS_RENAMED)
    source = frozen_source()
    for row in A4:
        assert f"| {row['id']} |" in source


def test_edcx_a4_renamed_ivp_is_solved_and_verified():
    """ED-T-17: `y'+2y=e^{-t}, y(0)=1` con `t -> x`; solución `e^{-x}`."""
    expression = BACKEND_INPUT["ED-T-17"]
    with TestClient(app) as client:
        response = client.post("/api/v1/ode", json={"expression": expression})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body.get("error_message")
    assert body["operation"] == "ode"

    parsed = sympy.sympify(body["result_text"], locals={"y": Y, "x": X})
    assert isinstance(parsed, sympy.Eq)
    rhs = parsed.rhs
    assert not rhs.has(Y(X))

    equation, ics, order = ode_service._parse_ode_text(expression)
    assert order == 1
    assert ics == {Y(0): sympy.Integer(1)}

    replacements = {Y(X): rhs, sympy.Derivative(Y(X), X): sympy.diff(rhs, X)}
    residual = sympy.simplify((equation.lhs - equation.rhs).subs(replacements).doit())
    assert residual == 0, f"residuo {residual}"
    assert sympy.simplify(rhs.subs(X, 0) - 1) == 0
    assert sympy.simplify(rhs - sympy.exp(-X)) == 0, f"{rhs} != exp(-x)"


def test_edcx_a4_convolution_row_returns_a_product_not_a_convolution():
    """ED-T-16: no hay operación de convolución; `t*exp(t)` se devuelve literal."""
    t = sympy.Symbol("t")
    with TestClient(app) as client:
        integral = client.post(
            "/api/v1/evaluate",
            json={"expression": "integrate(tau*exp(t-tau),tau,0,t)"},
        ).json()
        product = client.post("/api/v1/evaluate", json={"expression": "t*exp(t)"}).json()
    assert integral["success"] is False
    assert integral["error_code"] == "PARSE_ERROR"
    assert "integrate" in (integral.get("error_message") or "")

    assert product["success"] is True, product
    literal = sympy.sympify(product["result_text"])
    expected = sympy.exp(t) - t - 1
    assert sympy.simplify(literal - expected) != 0, "el producto no debe coincidir con la convolución"
    assert literal == t * sympy.exp(t)


def test_edcx_a4_documented_semicolon_second_ic_is_not_implemented():
    """Defecto medido: `_parse_initial_condition` documenta `;` pero no lo parte."""
    expression = "y''-y=exp(x), y(0)=0; y'(0)=0"
    with pytest.raises(ode_service.ODEParseError, match="No se pudo interpretar"):
        ode_service._parse_ode_text(expression)
    with TestClient(app) as client:
        body = client.post("/api/v1/ode", json={"expression": expression}).json()
    assert body["success"] is False
    assert body["error_code"] == "PARSE_ERROR"
    assert "No se pudo interpretar" in (body.get("error_message") or "")


@pytest.mark.parametrize("row", [r for r in A4 if r["id"] in BLOCKED], ids=lambda r: r["id"])
def test_edcx_a4_blocked_rows_fail_explicitly_and_fast(row: dict):
    started = time.monotonic()
    with TestClient(app) as client:
        for path, expression, expected_code, fragment in BLOCKED[row["id"]]:
            response = client.post(path, json={"expression": expression})
            assert response.status_code == 200, (row["id"], response.text)
            body = response.json()
            assert body["success"] is False, (row["id"], expression, body)
            assert body["error_code"] == expected_code, (row["id"], expression, body)
            assert fragment in (body.get("error_message") or ""), (row["id"], expression, body)
    elapsed = time.monotonic() - started
    assert elapsed < 15.0, f"{row['id']} tardó {elapsed:.1f}s"
