"""EDCX Parte A · A1 "Primer orden" (53 filas): certificación contra /api/v1/ode.

Contrato de canal
-----------------
La fuente congelada escribe los ejercicios en LaTeX (`\\frac{dy}{dx}=...`,
`(2xy+3)\\,dx+(x^2-1)\\,dy=0`). El canal real del producto es el campo único de
`BasicMode.tsx`, que normaliza a sintaxis de backend (notación prima `y'` y
producto explícito) antes de llamar a `/ode`. `BACKEND_INPUT` documenta esa
normalización fila por fila, sin alterar el ejercicio ni el resultado esperado.

Oráculo
-------
Independiente de `dsolve`: la solución devuelta se sustituye en la EDO y en la
condición inicial. Se aceptan soluciones explícitas e implícitas; nunca se
compara texto contra la columna "Resultado esperado".

Clasificación
-------------
- Filas resueltas: PASS si la familia satisface la EDO (y la condición inicial).
  Las filas cuyo esperado incluye además soluciones singulares se registran como
  F4 (correcto pero incompleto) en `MANUAL_CAPABILITY_GAPS.md`, no como FAIL.
- Filas fuera del alcance de `sympy.dsolve` o que agotan el plazo: BLOCKED con
  error explícito (`UNSUPPORTED_OPERATION`/`TIMEOUT`) y tiempo acotado; jamás se
  cuentan como PASS.
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
A1 = [row for row in ROWS if row["bloque"] == "A1"]

X = sympy.Symbol("x")
Y = sympy.Function("y")
DY = sympy.Derivative(Y(X), X)
C1 = sympy.Symbol("C1")
PARAM_VALUES = {
    "r": sympy.Rational(1, 2),
    "K": sympy.Integer(4),
    "y0": sympy.Integer(1),
    "C1": sympy.Rational(13, 10),
}

# Normalización documentada LaTeX (fuente) -> sintaxis de backend (canal real).
BACKEND_INPUT = {
    "ED-S-01": "y'=y",
    "ED-S-02": "y'=x*y",
    "ED-S-03": "y'=x/y",
    "ED-S-04": "y'=y^2",
    "ED-S-05": "y'=exp(x-y)",
    "ED-S-06": "y'=(1+y^2)/(1+x^2)",
    "ED-S-07": "x*y'=y*ln(y)",
    "ED-S-08": "y'=y^2-1",
    "ED-S-09": "y'=2*x*y, y(0)=3",
    "ED-S-10": "y'=y/x, y(1)=2",
    "ED-S-11": "y'=-x/y, y(0)=2",
    "ED-S-12": "y'=(1+y^2)*cos(x), y(0)=0",
    "ED-S-13": "y'=sqrt(y)",
    "ED-S-14": "y'=y^(1/3), y(0)=0",
    "ED-L-01": "y'+y=exp(x)",
    "ED-L-02": "y'+2*y=x",
    "ED-L-03": "y'+y=sin(x)",
    "ED-L-04": "x*y'+y=x^2",
    "ED-L-05": "y'-2*y/x=x^2",
    "ED-L-06": "y'+y*tan(x)=sin(x)",
    "ED-L-07": "(x^2+1)*y'+2*x*y=x",
    "ED-L-08": "y'+y/x=sin(x)/x",
    "ED-L-09": "y'+3*y=6, y(0)=0",
    "ED-L-10": "y'+y=x, y(0)=1",
    "ED-L-11": "y'+2*x*y=exp(-x^2), y(0)=1",
    # ED-L-12 pide x(y): el canal y el motor son y(x); capability gap explícito.
    "ED-L-12": None,
    "ED-H-01": "y'=(x+y)/x",
    "ED-H-02": "y'=y/x+x/y",
    "ED-H-03": "(x^2+y^2)-2*x*y*y'=0",
    "ED-H-04": "y'=2*x*y/(x^2-y^2)",
    "ED-H-05": "x*y'=y+sqrt(x^2+y^2)",
    "ED-H-06": "(x+y+1)+(2*x+2*y-1)*y'=0",
    "ED-X-01": "(2*x*y+3)+(x^2-1)*y'=0",
    "ED-X-02": "(3*x^2*y+y^3)+(x^3+3*x*y^2)*y'=0",
    "ED-X-03": "(y*cos(x)+2*x*exp(y))+(sin(x)+x^2*exp(y)-1)*y'=0",
    "ED-X-04": "(2*x*y+y^2)+(x^2+2*x*y)*y'=0",
    "ED-X-05": "(2*x+y)+(x+2*y)*y'=0, y(1)=1",
    "ED-X-06": "y+(2*x-y*exp(y))*y'=0",
    "ED-X-07": "(x^2+y^2+x)+x*y*y'=0",
    "ED-B-01": "y'+y=x*y^2",
    "ED-B-02": "y'=y+y^2, y(0)=1",
    "ED-B-03": "y'-y/x=y^3",
    "ED-B-04": "x*y'+y=x^2*y^2*ln(x)",
    "ED-B-05": "y'=r*y*(1-y/K)",
    "ED-B-06": "y'=r*y*(1-y/K), y(0)=y0",
    "ED-B-07": "y'=1+x^2-2*x*y+y^2",
    "ED-B-08": "y'=y^2-2/x^2",
    "ED-B-09": "y'=y^2-x",
    "ED-C-01": "y=x*y'+y'^2",
    "ED-C-02": "y=x*y'+1/y'",
    "ED-C-03": "y'^2-4*y'+3=0",
    "ED-C-04": "y'^2=y",
    "ED-C-05": "y=2*x*y'+y'^2",
}

# Filas que hoy devuelven un error explícito (medido en HEAD, no asumido).
# ED-X-02/X-03 y ED-C-02 no terminan ni en 30 s; ED-C-05 tarda ~20 s y acaba en
# UNSUPPORTED_OPERATION. Con el plazo por defecto (8 s) el error es TIMEOUT.
KNOWN_LIMITS = {
    "ED-L-12": "CHANNEL_UNSUPPORTED",
    "ED-X-02": "BOUNDED_ERROR",
    "ED-X-03": "BOUNDED_ERROR",
    "ED-B-09": "BOUNDED_ERROR",
    "ED-C-02": "BOUNDED_ERROR",
    "ED-C-05": "BOUNDED_ERROR",
}

# Resoluble pero lento (ED-X-04: ~4,7 s en HEAD): se certifica con un plazo
# ampliado explícito para no confundir latencia con corrección.
SLOW_SOLVABLE = {"ED-X-04"}

# Filas con raíz cúbica real: `y^(1/3)` de SymPy es la rama principal compleja,
# así que el oráculo usa la semántica real documentada (signo preservado).
REAL_BRANCH = {"ED-S-14"}

# Filas cuya familia es correcta pero el resultado esperado incluye, además,
# soluciones singulares o ramas que `dsolve` no enumera (F4, documentado).
F4_INCOMPLETE = {"ED-S-04", "ED-S-08", "ED-S-13", "ED-S-14", "ED-B-01", "ED-C-01", "ED-C-03", "ED-C-04"}

SAMPLES = (0.11, 0.23, 0.41, 0.67, 1.13, 1.79, 2.37, -0.37, -1.13)


def frozen_lines() -> str:
    import gzip

    return gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")


def _post(client: TestClient, expression: str) -> dict:
    response = client.post("/api/v1/ode", json={"expression": expression})
    assert response.status_code == 200, response.text
    return response.json()


def _as_solution(body: dict) -> sympy.Eq:
    parsed = sympy.sympify(body["result_text"], locals={"y": Y, "x": X})
    assert isinstance(parsed, sympy.Eq)
    return parsed


def _explicit_rhs(solution: sympy.Eq):
    rhs = solution.rhs
    return rhs if not rhs.has(Y(X)) else None


def _numeric_residual(expression: str, rhs) -> tuple[int, float]:
    """Sustituye y(x)=rhs en la EDO y devuelve (muestras válidas, peor residuo)."""
    equation, _, _ = ode_service._parse_ode_text(expression)
    rhs = rhs.subs(PARAM_VALUES)
    derivative = sympy.diff(rhs, X)
    residual = (equation.lhs - equation.rhs).subs(PARAM_VALUES).subs(
        {Y(X): rhs, DY: derivative}
    ).doit()
    func = sympy.lambdify(X, residual, "mpmath")
    valid, worst = 0, 0.0
    for point in SAMPLES:
        try:
            value = complex(func(point))
        except Exception:  # noqa: BLE001 - fuera de dominio/rama de la solución
            continue
        if not (abs(value) == abs(value)) or abs(value) == float("inf"):
            continue
        valid += 1
        worst = max(worst, abs(value))
    return valid, worst


def _real_cbrt_residual(expression: str, rhs) -> tuple[int, float]:
    """Oráculo de rama real para `y'=y^(1/3)`: |y'|³ = |y| y mismo signo."""
    rhs = rhs.subs(PARAM_VALUES)
    derivative = sympy.diff(rhs, X)
    dfunc = sympy.lambdify(X, derivative, "mpmath")
    yfunc = sympy.lambdify(X, rhs, "mpmath")
    valid, worst = 0, 0.0
    for point in SAMPLES:
        try:
            d = complex(dfunc(point))
            value = complex(yfunc(point))
        except Exception:  # noqa: BLE001
            continue
        if abs(d.imag) > 1e-12 or abs(value.imag) > 1e-12:
            continue
        if abs(value) == float("inf") or abs(d) == float("inf"):
            continue
        # y' = y^(1/3) real  <=>  |y'|³ = |y| y signo(y') = signo(y)
        residual = abs(abs(d.real) ** 3 - abs(value.real))
        if d.real * value.real < 0:
            residual += 1.0
        valid += 1
        worst = max(worst, residual)
    return valid, worst


def _implicit_residual(expression: str, solution: sympy.Eq) -> tuple[int, float]:
    """F(x,y)=0: verifica F_x + F_y·y' = 0 con y' despejada de la EDO."""
    equation, _, _ = ode_service._parse_ode_text(expression)
    closed = sympy.solve(equation, DY)
    assert len(closed) == 1, f"oráculo implícito requiere y' única: {closed}"
    dydx = closed[0].subs(Y(X), Y).subs(PARAM_VALUES)
    form = (solution.lhs - solution.rhs).subs(Y(X), Y).subs(PARAM_VALUES)
    total = sympy.diff(form, X) + sympy.diff(form, Y) * dydx
    func = sympy.lambdify((X, Y), total, "mpmath")
    # Puntos sobre la curva: se resuelve y numéricamente para cada x muestreada.
    valid, worst = 0, 0.0
    for point in SAMPLES:
        try:
            branches = sympy.solve(form.subs(X, sympy.Float(point)), Y)
        except Exception:  # noqa: BLE001
            continue
        for branch in branches:
            if not branch.is_real:
                continue
            try:
                value = complex(func(point, float(branch)))
            except Exception:  # noqa: BLE001
                continue
            if abs(value) != abs(value) or abs(value) == float("inf"):
                continue
            valid += 1
            worst = max(worst, abs(value))
    return valid, worst


def _check_initial_condition(expression: str, solution: sympy.Eq) -> None:
    _, ics, _ = ode_service._parse_ode_text(expression)
    if not ics:
        return
    rhs = _explicit_rhs(solution)
    if rhs is None:
        return
    for condition, value in ics.items():
        point = condition.args[0]
        got = sympy.N(rhs.subs(PARAM_VALUES).subs(X, point))
        expected = sympy.N(sympy.sympify(value).subs(PARAM_VALUES))
        assert abs(complex(got) - complex(expected)) < 1e-6, f"IC {condition}={value} -> {got}"


def test_edcx_fixture_a1_matches_the_frozen_source():
    assert len(ROWS) == 638
    assert len(A1) == 53
    assert set(BACKEND_INPUT) == {row["id"] for row in A1}
    source = frozen_lines()
    for row in A1:
        assert f"| {row['id']} |" in source
    # Distribución por subbloque del documento congelado.
    counts: dict[str, int] = {}
    for row in A1:
        counts[row["subbloque"]] = counts.get(row["subbloque"], 0) + 1
    assert counts == {"S": 14, "L": 12, "H": 6, "X": 7, "B": 9, "C": 5}
    ids = {row["id"] for row in A1}
    assert F4_INCOMPLETE <= ids
    assert set(KNOWN_LIMITS) <= ids
    assert SLOW_SOLVABLE <= ids
    assert not (set(F4_INCOMPLETE) & set(KNOWN_LIMITS))
    assert not (set(KNOWN_LIMITS) & SLOW_SOLVABLE)


@pytest.mark.parametrize(
    "row",
    [r for r in A1 if r["id"] not in KNOWN_LIMITS and r["id"] not in SLOW_SOLVABLE],
    ids=lambda r: r["id"],
)
def test_edcx_a1_solution_satisfies_the_ode(row: dict):
    expression = BACKEND_INPUT[row["id"]]
    with TestClient(app) as client:
        body = _post(client, expression)
    assert body["success"] is True, body.get("error_message")
    assert body["operation"] == "ode"
    assert body["result_type"] == "ode_solution"
    solution = _as_solution(body)
    rhs = _explicit_rhs(solution)
    if rhs is not None:
        oracle = _real_cbrt_residual if row["id"] in REAL_BRANCH else _numeric_residual
        valid, worst = oracle(expression, rhs)
        assert valid >= 3, f"sin muestras válidas para {row['id']}"
        assert worst < 1e-7, f"{row['id']} residuo {worst:g}"
    else:
        valid, worst = _implicit_residual(expression, solution)
        assert valid >= 3, f"sin muestras válidas (implícita) para {row['id']}"
        assert worst < 1e-6, f"{row['id']} residuo implícito {worst:g}"
    _check_initial_condition(expression, solution)


@pytest.mark.parametrize("row", [r for r in A1 if r["id"] in SLOW_SOLVABLE], ids=lambda r: r["id"])
def test_edcx_a1_slow_but_solvable_rows_are_correct(row: dict, monkeypatch):
    monkeypatch.setenv("ODE_SOLVE_TIMEOUT_SECONDS", "25")
    expression = BACKEND_INPUT[row["id"]]
    with TestClient(app) as client:
        body = _post(client, expression)
    assert body["success"] is True, body.get("error_message")
    valid, worst = _numeric_residual(expression, _explicit_rhs(_as_solution(body)))
    assert valid >= 3
    assert worst < 1e-7


@pytest.mark.parametrize("row", [r for r in A1 if r["id"] in KNOWN_LIMITS], ids=lambda r: r["id"])
def test_edcx_a1_known_limits_are_explicit_and_bounded(row: dict, monkeypatch):
    expected = KNOWN_LIMITS[row["id"]]
    expression = BACKEND_INPUT[row["id"]]
    if expression is None:
        pytest.skip("sin canal y(x): capability gap de canal, no de motor")
    monkeypatch.setenv("ODE_SOLVE_TIMEOUT_SECONDS", "3")
    started = time.monotonic()
    with TestClient(app) as client:
        body = _post(client, expression)
    elapsed = time.monotonic() - started
    assert expected == "BOUNDED_ERROR"
    assert body["success"] is False
    assert body["error_code"] in {"TIMEOUT", "UNSUPPORTED_OPERATION"}
    assert body["error_message"]
    assert elapsed < 20.0, f"{row['id']} tardó {elapsed:.1f}s"


def test_edcx_a1_timeout_is_bounded_and_pool_recovers(monkeypatch):
    monkeypatch.setenv("ODE_SOLVE_TIMEOUT_SECONDS", "3")
    with TestClient(app) as client:
        started = time.monotonic()
        timed_out = _post(client, BACKEND_INPUT["ED-X-02"])
        first = time.monotonic() - started
        assert timed_out["success"] is False
        assert timed_out["error_code"] == "TIMEOUT"
        assert first < 20.0
        recovered = _post(client, "y'=y")
        assert recovered["success"] is True
        assert recovered["result_text"] == "Eq(y(x), C1*exp(x))"
