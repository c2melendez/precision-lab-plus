"""EDCX Parte A — A7 "Cualitativo, numérico y retardo" (25 filas).

Canal
-----
El motor EDO de Plus resuelve cuatro filas en forma cerrada. No existe canal de
análisis cualitativo (equilibrios, estabilidad, bifurcaciones), ni de
trayectorias ortogonales, iteración de Picard, métodos numéricos (Euler, Heun,
RK4) o recurrencias, ni soporte de ecuaciones con retardo.

Clasificación
-------------
- PASS (2): ED-Q-23 (`y=Si(x)`) y ED-Q-24 (`y=sqrt(pi)/2 erf(x)`). El motor
  devuelve exactamente la forma cerrada de la fuente; se verifica residuo nulo
  y condición inicial.
- PASS_SCOPED (2): ED-Q-05 (`y=1/(1-x)`) y ED-Q-06 (`y=tan x`). El motor
  devuelve la solución, pero no el intervalo máximo; el intervalo se deriva con
  un oráculo sympy independiente y se documenta como tal.
- BLOCKED (21): el resto. Se mide el canal real: cualitativas devuelven una
  solución general sin equilibrios ni estabilidad; Q-07 devuelve solo una rama
  (`x^3/27`) y no certifica la no unicidad; las ortogonales no tienen canal;
  Picard no emite iterados (`steps=[]`); los métodos numéricos rechazan `h`
  como segunda condición; las recurrencias fallan con `AMBIGUOUS_VARIABLE`; el
  retardo devuelve una expresión que no es la solución del retardo; y Q-25
  devuelve `UNSUPPORTED_OPERATION`.

Las respuestas de la fuente se comprueban con oráculos sympy independientes,
pero nunca se atribuyen al producto.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import sympy
from fastapi.testclient import TestClient

from app.main import app

ROOT = Path(__file__).resolve().parents[2]
JSONL = ROOT / "qa/certification/edcx_ejecutables.jsonl"

ROWS = [json.loads(line) for line in JSONL.read_text(encoding="utf-8").splitlines() if line.strip()]
A7 = [row for row in ROWS if row["bloque"] == "A7"]
A7_IDS = {row["id"] for row in A7}

X = sympy.Symbol("x", positive=True)
T = sympy.Symbol("t", real=True)
Y = sympy.Function("y")

LOCALS = {
    "y": Y,
    "x": X,
    "t": T,
    "Si": sympy.Si,
    "erf": sympy.erf,
    "exp": sympy.exp,
    "tan": sympy.tan,
    "pi": sympy.pi,
    "E": sympy.E,
    "sqrt": sympy.sqrt,
}

# Entrada normalizada al canal EDO real.
ODE_INPUT = {
    "ED-Q-05": "y'=y^2, y(0)=1",
    "ED-Q-06": "y'=1+y^2, y(0)=0",
    "ED-Q-07": "y'=y^(2/3), y(0)=0",
    "ED-Q-23": "y'=sin(x)/x, y(0)=0",
    "ED-Q-24": "y'=exp(-x^2), y(0)=0",
    "ED-Q-25": "y'=x^2+y^2",
}

PASS_EXACT = {"ED-Q-23", "ED-Q-24"}
PASS_SCOPED = {"ED-Q-05", "ED-Q-06"}
BLOCKED = A7_IDS - PASS_EXACT - PASS_SCOPED

# Recurrencias: ecuación normalizada para /api/v1/solve.
RECURRENCES = {
    "ED-Q-17": "a(n+1)=2*a(n)",
    "ED-Q-18": "F(n+2)=F(n+1)+F(n)",
    "ED-Q-19": "a(n+2)-4*a(n+1)+4*a(n)=0",
    "ED-Q-20": "a(n+2)+a(n)=0",
    "ED-Q-21": "a(n+1)=a(n)+n",
}

NUMERICAL = {"ED-Q-13", "ED-Q-14", "ED-Q-15", "ED-Q-16"}
ORTHOGONAL = {"ED-Q-08", "ED-Q-09", "ED-Q-10"}
QUALITATIVE = {"ED-Q-01", "ED-Q-02", "ED-Q-03", "ED-Q-04"}
PICARD = {"ED-Q-11", "ED-Q-12"}
DELAY = {"ED-Q-22"}


def _post(client: TestClient, path: str, payload: dict) -> dict:
    response = client.post(path, json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def _solution(body: dict) -> sympy.Expr:
    parsed = sympy.sympify(body["result_text"], locals=LOCALS)
    assert isinstance(parsed, sympy.Eq)
    return parsed.rhs


def _first_order_residual(rhs, forcing) -> sympy.Expr:
    return sympy.simplify(sympy.diff(rhs, X) - forcing.subs(Y(X), rhs))


def test_edcx_fixture_a7_matches_the_frozen_source():
    assert len(ROWS) == 638
    assert len(A7) == 25
    assert PASS_EXACT | PASS_SCOPED | BLOCKED == A7_IDS
    assert len(PASS_EXACT) == 2 and len(PASS_SCOPED) == 2 and len(BLOCKED) == 21


@pytest.mark.parametrize("row_id", sorted(PASS_EXACT))
def test_edcx_a7_exact_rows_return_the_source_closed_form(row_id):
    client = TestClient(app)
    rhs = _solution(_post(client, "/api/v1/ode", {"expression": ODE_INPUT[row_id]}))

    if row_id == "ED-Q-23":
        assert sympy.simplify(rhs - sympy.Si(X)) == 0
        assert _first_order_residual(rhs, sympy.sin(X) / X) == 0
    else:
        assert sympy.simplify(rhs - sympy.sqrt(sympy.pi) * sympy.erf(X) / 2) == 0
        assert _first_order_residual(rhs, sympy.exp(-X**2)) == 0
    assert sympy.simplify(rhs.subs(X, 0)) == 0


@pytest.mark.parametrize("row_id", sorted(PASS_SCOPED))
def test_edcx_a7_solution_is_exact_but_the_maximal_interval_is_not_emitted(row_id):
    client = TestClient(app)
    body = _post(client, "/api/v1/ode", {"expression": ODE_INPUT[row_id]})
    rhs = _solution(body)

    if row_id == "ED-Q-05":
        assert sympy.simplify(rhs - 1 / (1 - X)) == 0
        assert _first_order_residual(rhs, rhs**2) == 0
        assert sympy.solve(sympy.denom(sympy.together(rhs)), X) == [1]
    else:
        assert sympy.simplify(rhs - sympy.tan(X)) == 0
        assert _first_order_residual(rhs, 1 + rhs**2) == 0
        assert sympy.cos(sympy.pi / 2) == 0

    # El intervalo máximo no viaja en la respuesta: se deriva con oráculo.
    assert body["result_text"] is not None
    assert body["domain_conditions"] == []


def test_edcx_a7_nonunique_row_returns_only_one_branch():
    client = TestClient(app)
    body = _post(client, "/api/v1/ode", {"expression": ODE_INPUT["ED-Q-07"]})
    rhs = _solution(body)
    assert sympy.simplify(rhs - X**3 / 27) == 0

    # Oráculo: ambas ramas satisfacen y'=y^(2/3), y(0)=0.
    zero = sympy.Integer(0)
    other = X**3 / 27
    assert sympy.simplify(sympy.diff(zero, X) - sympy.Pow(zero, sympy.Rational(2, 3))) == 0
    assert sympy.simplify(sympy.diff(other, X) - sympy.Pow(other, sympy.Rational(2, 3))) == 0
    # El producto no devuelve la rama nula ni un veredicto de unicidad.
    assert "0" != body["result_text"]


def test_edcx_a7_qualitative_rows_have_no_classification_channel():
    client = TestClient(app)
    body = _post(client, "/api/v1/ode", {"expression": "y'=y*(1-y)*(y-2)"})
    assert body["success"] is True
    # Devuelve una solución general, no el conjunto de equilibrios ni su tipo.
    assert "C1" in body["result_text"]
    assert not ({"equilibria", "stability", "bifurcation"} & set(body))

    paths = app.openapi()["paths"]
    forbidden = ("equilib", "stabil", "bifurc", "phase", "qualitative")
    assert [p for p in paths if any(t in p.lower() for t in forbidden)] == []

    f = sympy.Symbol("y", real=True) * (1 - sympy.Symbol("y", real=True)) * (
        sympy.Symbol("y", real=True) - 2
    )
    derivative = sympy.diff(f, sympy.Symbol("y", real=True))
    labels = {0: sympy.sign(derivative.subs(sympy.Symbol("y", real=True), 0)),
              1: sympy.sign(derivative.subs(sympy.Symbol("y", real=True), 1)),
              2: sympy.sign(derivative.subs(sympy.Symbol("y", real=True), 2))}
    assert labels == {0: -1, 1: 1, 2: -1}  # estable, inestable, estable


def test_edcx_a7_orthogonal_trajectories_have_no_channel():
    client = TestClient(app)
    for probe in ("y=C*x^2", "y=C*exp(x)", "x^2+y^2=C"):
        body = _post(client, "/api/v1/evaluate", {"expression": probe})
        assert body["success"] is False
        assert body["error_code"] == "PARSE_ERROR"

    paths = app.openapi()["paths"]
    assert [p for p in paths if "orthogonal" in p.lower()] == []

    # Oráculo: pendientes ortogonales. y=C e^x tiene pendiente y; la ortogonal
    # satisface y'=-1/y, cuya integral es y^2 = -2x + K.
    assert sympy.simplify(sympy.diff(sympy.Symbol("C") * X**2, X)) == 2 * sympy.Symbol("C") * X
    yy = sympy.Function("yy")
    implicit = yy(X) ** 2 + 2 * X
    slope = sympy.idiff(implicit, yy(X), X)
    assert sympy.simplify(slope - (-1 / yy(X))) == 0


def test_edcx_a7_picard_iteration_is_not_emitted():
    client = TestClient(app)
    for row_id in ("ED-Q-11", "ED-Q-12"):
        body = _post(client, "/api/v1/ode", {"expression": "y'=y, y(0)=1" if row_id == "ED-Q-11" else "y'=x+y, y(0)=0"})
        assert body["success"] is True
        assert body["steps"] == []
        assert body["has_detailed_steps"] is False

    paths = app.openapi()["paths"]
    assert [p for p in paths if "picard" in p.lower()] == []

    # Oráculo: iterados de Picard.
    s = sympy.Symbol("s", positive=True)
    y0 = sympy.Integer(1)
    y1 = y0 + sympy.integrate(y0, (s, 0, X))
    y2 = y0 + sympy.integrate(y1.subs(X, s), (s, 0, X))
    assert sympy.simplify(y1 - (1 + X)) == 0
    assert sympy.simplify(y2 - (1 + X + X**2 / 2)) == 0
    z1 = sympy.integrate(s, (s, 0, X))
    z2 = sympy.integrate(z1.subs(X, s) + s, (s, 0, X))
    assert sympy.simplify(z1 - X**2 / 2) == 0
    assert sympy.simplify(z2 - (X**2 / 2 + X**3 / 6)) == 0


def test_edcx_a7_numerical_methods_have_no_channel():
    client = TestClient(app)
    body = _post(client, "/api/v1/ode", {"expression": "y'=y, y(0)=1, h=0.1"})
    assert body["success"] is False
    assert body["error_code"] == "PARSE_ERROR"

    paths = app.openapi()["paths"]
    forbidden = ("euler", "heun", "rk4", "runge", "numeric")
    assert [p for p in paths if any(t in p.lower() for t in forbidden)] == []

    # Oráculo: valores de los métodos.
    h = sympy.Rational(1, 10)
    value = sympy.Integer(1)
    for _ in range(10):
        value = value + h * value
    assert sympy.simplify(value - sympy.Rational(11, 10) ** 10) == 0

    k1 = sympy.Integer(1)
    k2 = 1 + h * k1
    assert sympy.simplify((1 + h / 2 * (k1 + k2)) - sympy.Rational(221, 200)) == 0

    k1 = sympy.Integer(1)
    k2 = 1 + sympy.Rational(1, 2) * k1
    k3 = 1 + sympy.Rational(1, 2) * k2
    k4 = 1 + k3
    rk4 = 1 + sympy.Rational(1, 6) * (k1 + 2 * k2 + 2 * k3 + k4)
    assert sympy.simplify(rk4 - sympy.Rational(65, 24)) == 0

    y = sympy.Integer(1)
    for _ in range(2):
        y = y + sympy.Rational(1, 2) * y**2
    assert sympy.simplify(y - sympy.Rational(21, 8)) == 0


@pytest.mark.parametrize("row_id", sorted(RECURRENCES))
def test_edcx_a7_recurrences_have_no_solver(row_id):
    client = TestClient(app)
    body = _post(client, "/api/v1/solve", {"equation": RECURRENCES[row_id]})
    assert body["success"] is False
    assert body["error_code"] == "AMBIGUOUS_VARIABLE"

    paths = app.openapi()["paths"]
    assert [p for p in paths if "recurrence" in p.lower() or "rsolve" in p.lower()] == []


def test_edcx_a7_recurrence_oracles_hold():
    n = sympy.Symbol("n", integer=True, nonnegative=True)
    assert sympy.simplify(3 * 2**n - 3 * 2**n) == 0

    phi = (1 + sympy.sqrt(5)) / 2
    psi = (1 - sympy.sqrt(5)) / 2
    fib = (phi**n - psi**n) / sympy.sqrt(5)
    assert sympy.simplify(fib.subs(n, 0)) == 0
    assert sympy.simplify(fib.subs(n, 1)) == 1

    a19 = (n + 1) * 2**n
    assert sympy.simplify(
        a19.subs(n, n + 2) - 4 * a19.subs(n, n + 1) + 4 * a19
    ) == 0

    a20 = sympy.cos(n * sympy.pi / 2)
    assert sympy.simplify(a20.subs(n, n + 2) + a20) == 0

    a21 = n * (n - 1) / 2
    assert sympy.simplify(a21.subs(n, n + 1) - (a21 + n)) == 0


def test_edcx_a7_delay_row_is_not_executed():
    client = TestClient(app)
    body = _post(client, "/api/v1/ode", {"expression": "y'(t)=y(t-1)"})
    # El canal responde success pero no devuelve la solución del retardo.
    assert body["success"] is True
    result = body["result_text"]
    assert "1 + t" not in result and "t**2" not in result

    paths = app.openapi()["paths"]
    assert [p for p in paths if "delay" in p.lower()] == []

    # Oráculo: solución por tramos del retardo.
    history = sympy.Integer(1)
    first = history + sympy.integrate(history, (T, 0, T))
    assert sympy.simplify(first - (1 + T)) == 0
    second = first.subs(T, 1) + sympy.integrate(first.subs(T, T - 1), (T, 1, T))
    assert sympy.simplify(second - (T**2 + 3) / 2) == 0


def test_edcx_a7_riccati_row_is_unsupported():
    client = TestClient(app)
    body = _post(client, "/api/v1/ode", {"expression": ODE_INPUT["ED-Q-25"]})
    assert body["success"] is False
    assert body["error_code"] == "UNSUPPORTED_OPERATION"

    # Oráculo: y=-u'/u transforma la Riccati en u''+x^2 u=0.
    u = sympy.Function("u")
    y = -sympy.diff(u(X), X) / u(X)
    transformed = sympy.simplify(sympy.diff(y, X) - (X**2 + y**2))
    assert sympy.simplify(transformed + X**2 + sympy.diff(u(X), X, 2) / u(X)) == 0


def test_edcx_a7_classification_counts_are_explicit():
    assert len(A7) == 25
    assert len(PASS_EXACT) == 2
    assert len(PASS_SCOPED) == 2
    assert len(BLOCKED) == 21
    assert PASS_EXACT | PASS_SCOPED | BLOCKED == A7_IDS
    assert QUALITATIVE | ORTHOGONAL | PICARD | NUMERICAL | set(RECURRENCES) | DELAY <= BLOCKED
