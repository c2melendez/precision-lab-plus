"""EDCX Parte A · A2 "Segundo orden y orden superior" (50 filas).

Canal
-----
La fuente congelada escribe LaTeX (`y''`, `y^{(4)}`, `W(...)`). El campo único
del producto solo habla la notación de backend: primas para las derivadas de
`y(x)` y producto explícito. `BACKEND_INPUT` documenta esa normalización fila a
fila. Las filas de Wronskiano se ejecutan por el canal real que sí las puede
resolver, `/matrix/determinant` (el wronskiano *es* el determinante de la matriz
fundamental); el canal `/ode` las rechaza porque no son una EDO.

Oráculo
-------
Independiente de `dsolve`: la solución devuelta se sustituye en la EDO (con sus
derivadas hasta el orden) y se exige residuo numérico nulo en varias muestras,
más el número correcto de constantes arbitrarias. Para los wronskianos, el
escalar devuelto se compara con el determinante calculado aquí derivando las
funciones, nunca con el texto de la columna "Resultado esperado".

Clasificación
-------------
- PASS: resuelto y verificado por el oráculo.
- BLOCKED_SCOPE: límite de producto medido (orden máximo 2, una sola condición
  inicial, sin operación de Wronskiano, funciones no admitidas en celdas).
  Nunca se cuenta como PASS.
- PASS_SCOPED: misma EDO con renombrado de variables (ED-A-05: el motor solo
  admite `y(x)`); se documenta el renombrado y se verifica la solución.
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
A2 = [row for row in ROWS if row["bloque"] == "A2"]

X = sympy.Symbol("x")
Y = sympy.Function("y")
C1, C2, C3 = sympy.symbols("C1 C2 C3")
PARAMS = {C1: sympy.Rational(13, 10), C2: sympy.Rational(7, 10), C3: sympy.Rational(4, 10)}

# Normalización documentada LaTeX (fuente) -> sintaxis del canal real.
BACKEND_INPUT = {
    "ED-K-01": "y''-3*y'+2*y=0",
    "ED-K-02": "y''+4*y=0",
    "ED-K-03": "y''+2*y'+y=0",
    "ED-K-04": "y''-4*y'+13*y=0",
    "ED-K-05": "y''+y'+y=0",
    "ED-K-06": "y'''-6*y''+11*y'-6*y=0",
    "ED-K-07": "y'''-y=0",
    "ED-K-08": "y''''-y=0",
    "ED-K-09": "y''''+2*y''+y=0",
    "ED-K-10": "y''''+4*y=0",
    "ED-K-11": "y''+y=0, y(0)=1, y'(0)=0",
    "ED-K-12": "y''+2*y'+5*y=0, y(0)=1, y'(0)=1",
    "ED-K-13": "y''-5*y'+6*y=0, y(0)=2, y'(0)=5",
    "ED-K-14": "y''+y=0, y(0)=0, y(pi)=0",
    "ED-K-15": "y''+y=0, y(0)=0, y(pi)=1",
    "ED-K-16": "y''+lambda*y=0, y(0)=0, y(pi)=0",
    "ED-N-01": "y''-y=x",
    "ED-N-02": "y''-3*y'+2*y=exp(3*x)",
    "ED-N-03": "y''-3*y'+2*y=exp(x)",
    "ED-N-04": "y''+y=sin(x)",
    "ED-N-05": "y''+2*y'+y=exp(-x)",
    "ED-N-06": "y''-2*y'+y=x*exp(x)",
    "ED-N-07": "y''+y'-2*y=x^2",
    "ED-N-08": "y''+2*y'+5*y=exp(-x)*cos(2*x)",
    "ED-N-09": "y''+y=tan(x)",
    "ED-N-10": "y''+y=sec(x)",
    "ED-N-11": "y''+y=csc(x)",
    "ED-N-12": "y''-2*y'+y=exp(x)/x",
    "ED-N-13": "y''+y=t, y(0)=0, y'(0)=0",
    "ED-N-14": "y''+4*y'+4*y=exp(-2*x), y(0)=0, y'(0)=0",
    "ED-N-15": "y'''-y''=1",
    "ED-E-01": "x^2*y''-2*y=0",
    "ED-E-02": "x^2*y''+x*y'-y=0",
    "ED-E-03": "x^2*y''-3*x*y'+4*y=0",
    "ED-E-04": "x^2*y''+x*y'+y=0",
    "ED-E-05": "x^2*y''-2*x*y'+2*y=x^3",
    "ED-E-06": "y*y''=y'^2",
    "ED-E-07": "y''+y'^2=0",
    "ED-E-08": "x*y''=y'",
    "ED-E-09": "x^2*y''-x*y'+y=0",
    # Wronskianos: no son EDO; el canal real es /matrix/determinant.
    "ED-E-10": None,
    "ED-E-11": None,
    "ED-E-12": None,
    "ED-E-13": None,
    "ED-E-14": None,
    "ED-A-01": "x''+9*x=0, x(0)=1, x'(0)=0",
    "ED-A-02": "x''+2*x'+10*x=0, x(0)=0, x'(0)=3",
    "ED-A-03": "x''+x=cos(t), x(0)=0, x'(0)=0",
    "ED-A-04": "x''+omega^2*x=cos(gamma*t), x(0)=0, x'(0)=0",
    # Renombrado T(t) -> y(x); A=Ta, B=T0 (ver docstring).
    "ED-A-05": "y'=-k*(y-A), y(0)=B",
}

# Wronskianos ejecutables por /matrix/determinant: matriz fundamental LaTeX ->
# filas del canal. El oráculo recalcula el determinante derivando las funciones.
WRONSKIAN = {
    "ED-E-10": ["cos(x)", "sin(x)"],
    "ED-E-12": ["1", "x", "x^2"],
    "ED-E-14": ["sin(2*x)", "sin(x)*cos(x)"],
}
WRONSKIAN_MATRIX = {
    "ED-E-10": [["cos(x)", "sin(x)"], ["-sin(x)", "cos(x)"]],
    "ED-E-12": [["1", "x", "x^2"], ["0", "1", "2*x"], ["0", "0", "2"]],
    "ED-E-14": [["sin(2*x)", "sin(x)*cos(x)"], ["2*cos(2*x)", "cos(2*x)"]],
}

# Wronskianos no ejecutables: ambas vías los rechazan (medido en HEAD).
MATRIX_ATTEMPTS = {
    "ED-E-11": [["exp(x)", "exp(2*x)"], ["exp(x)", "2*exp(2*x)"]],
    "ED-E-13": [["x", "x*log(x)"], ["1", "log(x)+1"]],
}

FROZEN_EXPECTED = {
    "ED-E-10": 1,
    "ED-E-12": 2,
    "ED-E-14": 0,
}

# Filas bloqueadas: código y fragmento del mensaje medidos en HEAD.
BLOCKED = {
    "ED-K-06": ("UNSUPPORTED_OPERATION", "Orden de EDO no soportado"),
    "ED-K-07": ("UNSUPPORTED_OPERATION", "Orden de EDO no soportado"),
    "ED-K-08": ("UNSUPPORTED_OPERATION", "Orden de EDO no soportado"),
    "ED-K-09": ("UNSUPPORTED_OPERATION", "Orden de EDO no soportado"),
    "ED-K-10": ("UNSUPPORTED_OPERATION", "Orden de EDO no soportado"),
    "ED-K-11": ("PARSE_ERROR", "condición inicial"),
    "ED-K-12": ("PARSE_ERROR", "condición inicial"),
    "ED-K-13": ("PARSE_ERROR", "condición inicial"),
    "ED-K-14": ("PARSE_ERROR", "condición inicial"),
    "ED-K-15": ("PARSE_ERROR", "condición inicial"),
    "ED-K-16": ("PARSE_ERROR", "condición inicial"),
    "ED-N-13": ("PARSE_ERROR", "condición inicial"),
    "ED-N-14": ("PARSE_ERROR", "condición inicial"),
    "ED-N-15": ("UNSUPPORTED_OPERATION", "Orden de EDO no soportado"),
    "ED-E-06": ("UNSUPPORTED_OPERATION", "no está dentro de los tipos soportados"),
    "ED-E-11": ("PARSE_ERROR", "funci"),
    "ED-E-13": ("PARSE_ERROR", "funci"),
    "ED-A-01": ("PARSE_ERROR", "condición inicial"),
    "ED-A-02": ("PARSE_ERROR", "condición inicial"),
    "ED-A-03": ("PARSE_ERROR", "condición inicial"),
    "ED-A-04": ("PARSE_ERROR", "condición inicial"),
}

POSITIVE_SAMPLES = (0.31, 0.57, 1.13, 1.79, 2.37, 3.11)
SAMPLES = (0.31, 0.57, 1.13, 1.79, 2.37, -0.37, -1.13)


def frozen_source() -> str:
    import gzip

    return gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")


def _post(client: TestClient, expression: str) -> dict:
    response = client.post("/api/v1/ode", json={"expression": expression})
    assert response.status_code == 200, response.text
    return response.json()


def _solution(body: dict) -> sympy.Eq:
    parsed = sympy.sympify(body["result_text"], locals={"y": Y, "x": X})
    assert isinstance(parsed, sympy.Eq)
    return parsed


def _order(expression: str) -> int:
    _, _, order = ode_service._parse_ode_text(expression)
    return order


def _residual_samples(expression: str, rhs, samples) -> tuple[int, float]:
    order = _order(expression)
    equation, ics, _ = ode_service._parse_ode_text(expression)
    assert ics is None  # las filas PASS de A2 no llevan condición inicial
    rhs = rhs.subs(PARAMS)
    replacements = {Y(X): rhs}
    for k in range(1, order + 1):
        replacements[sympy.Derivative(Y(X), (X, k))] = sympy.diff(rhs, X, k)
    residual = (equation.lhs - equation.rhs).subs(PARAMS).subs(replacements).doit()
    func = sympy.lambdify(X, residual, "mpmath")
    valid, worst = 0, 0.0
    for point in samples:
        try:
            value = complex(func(point))
        except Exception:  # noqa: BLE001 - fuera de dominio/rama
            continue
        if not (abs(value) == abs(value)) or abs(value) == float("inf"):
            continue
        valid += 1
        worst = max(worst, abs(value))
    return valid, worst


def _constants(rhs) -> int:
    return len([s for s in rhs.free_symbols if str(s).startswith("C") and str(s)[1:].isdigit()])


def _wronskian(functions: list[str]) -> sympy.Expr:
    exprs = [sympy.sympify(item.replace("^", "**")) for item in functions]
    matrix = sympy.Matrix([[sympy.diff(expr, X, k) for expr in exprs] for k in range(len(exprs))])
    return sympy.simplify(matrix.det())


def test_edcx_fixture_a2_matches_the_frozen_source():
    assert len(ROWS) == 638
    assert len(A2) == 50
    assert set(BACKEND_INPUT) == {row["id"] for row in A2}
    source = frozen_source()
    for row in A2:
        assert f"| {row['id']} |" in source
    ids = {row["id"] for row in A2}
    assert set(WRONSKIAN) <= ids
    assert set(BLOCKED) <= ids
    assert not (set(WRONSKIAN) & set(BLOCKED))
    passing = {
        rid for rid, expr in BACKEND_INPUT.items() if expr and rid not in BLOCKED
    }
    assert set(BACKEND_INPUT) == passing | set(WRONSKIAN) | set(BLOCKED)
    assert not (passing & set(BLOCKED))
    assert "ED-A-05" in passing


@pytest.mark.parametrize(
    "row",
    [r for r in A2 if r["id"] in BACKEND_INPUT and BACKEND_INPUT[r["id"]] and r["id"] not in BLOCKED and r["id"] != "ED-A-05"],
    ids=lambda r: r["id"],
)
def test_edcx_a2_solution_satisfies_the_ode(row: dict):
    expression = BACKEND_INPUT[row["id"]]
    with TestClient(app) as client:
        body = _post(client, expression)
    assert body["success"] is True, body.get("error_message")
    assert body["operation"] == "ode"
    solution = _solution(body)
    rhs = solution.rhs
    assert not rhs.has(Y(X)), f"{row['id']} devolvió solución implícita"
    samples = POSITIVE_SAMPLES if row["subbloque"] == "E" else SAMPLES
    valid, worst = _residual_samples(expression, rhs, samples)
    assert valid >= 3, f"sin muestras válidas para {row['id']}"
    assert worst < 1e-7, f"{row['id']} residuo {worst:g}"
    assert _constants(rhs) == _order(expression), f"{row['id']} familia incompleta"


@pytest.mark.parametrize("row", [r for r in A2 if r["id"] in WRONSKIAN], ids=lambda r: r["id"])
def test_edcx_a2_wronskian_determinant_matches_independent_derivation(row: dict):
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/matrix/determinant", json={"matrix": WRONSKIAN_MATRIX[row["id"]]}
        )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body.get("error_message")
    assert body["operation"] == "matrix_determinant"
    returned = sympy.sympify(body["result_text"])
    expected = _wronskian(WRONSKIAN[row["id"]])
    assert sympy.simplify(returned - expected) == 0, f"{row['id']}: {returned} != {expected}"
    assert sympy.simplify(returned - FROZEN_EXPECTED[row["id"]]) == 0


@pytest.mark.parametrize("row", [r for r in A2 if r["id"] in BLOCKED], ids=lambda r: r["id"])
def test_edcx_a2_blocked_rows_fail_explicitly_and_fast(row: dict):
    expected_code, fragment = BLOCKED[row["id"]]
    expression = BACKEND_INPUT[row["id"]]
    if expression is None:  # wronskiano no admitido por el parser de matrices
        with TestClient(app) as client:
            ode = _post(client, "W(cos(x),sin(x))")
            assert ode["success"] is False
            assert ode["error_code"] == "PARSE_ERROR"
            matrix = client.post(
                "/api/v1/matrix/determinant",
                json={"matrix": MATRIX_ATTEMPTS[row["id"]]},
            ).json()
            assert matrix["success"] is False
            assert matrix["error_code"] == expected_code
            assert fragment in (matrix.get("error_message") or "")
        return
    started = time.monotonic()
    with TestClient(app) as client:
        body = _post(client, expression)
    elapsed = time.monotonic() - started
    assert body["success"] is False
    assert body["error_code"] == expected_code, body
    assert fragment in (body.get("error_message") or ""), body
    assert elapsed < 10.0, f"{row['id']} tardó {elapsed:.1f}s"


def test_edcx_a2_renamed_thermal_row_is_the_same_ode():
    """ED-A-05: T'=-k(T-Ta), T(0)=T0 sólo difiere en nombres; el motor es y(x)."""
    expression = BACKEND_INPUT["ED-A-05"]
    with TestClient(app) as client:
        body = _post(client, expression)
    assert body["success"] is True, body.get("error_message")
    solution = _solution(body)
    k, A, B = sympy.symbols("k A B")
    numeric = {k: sympy.Rational(3, 5), A: sympy.Rational(8, 5), B: sympy.Integer(3)}
    rhs = solution.rhs.subs(numeric)
    equation = sympy.Eq(
        sympy.diff(Y(X), X), -numeric[k] * (Y(X) - numeric[A])
    )
    residual = (equation.lhs - equation.rhs).subs(Y(X), rhs).doit()
    func = sympy.lambdify(X, residual, "mpmath")
    for point in SAMPLES:
        assert abs(complex(func(point))) < 1e-12
    # Condición inicial y forma cerrada esperada A+(B-A)e^{-kx}.
    assert abs(complex(rhs.subs(X, 0)) - complex(numeric[B])) < 1e-12
    expected = numeric[A] + (numeric[B] - numeric[A]) * sympy.exp(-numeric[k] * X)
    assert sympy.simplify(rhs - expected) == 0, f"{rhs} != {expected}"
