"""EDCX Parte A — A8 "Casos límite" (6 filas).

Canal
-----
El motor EDO resuelve EDO con una condición inicial, pero no hace análisis de
existencia/unicidad, no representa familias paramétricas, no emite la solución
por ramas de una ecuación no lineal y no valida el intervalo máximo antes de
evaluar.

Clasificación
-------------
- BLOCKED (6): las seis filas. CL-01 y CL-02 (misma EDO, distinta condición)
  reciben exactamente el mismo `UNSUPPORTED_OPERATION`: el canal no distingue
  «sin solución» de «infinitas soluciones». CL-03 devuelve una integral sin
  evaluar, no el par no único. CL-04 devuelve `1/(1-x)` y al sustituir `x=2`
  responde `-1` con `success=true` (solo anota `x != 1`), sin el error claro que
  la fila exige. CL-05 devuelve una sola rama (`-|x|`), no `y=±x`. CL-06 tiene
  dos condiciones de frontera y se rechaza por el límite de una condición.

Las respuestas de la fuente se comprueban con oráculos sympy independientes,
pero nunca se atribuyen al producto.
"""
from __future__ import annotations

import json
from pathlib import Path

import sympy
from fastapi.testclient import TestClient

from app.main import app

ROOT = Path(__file__).resolve().parents[2]
JSONL = ROOT / "qa/certification/edcx_ejecutables.jsonl"

ROWS = [json.loads(line) for line in JSONL.read_text(encoding="utf-8").splitlines() if line.strip()]
A8 = [row for row in ROWS if row["bloque"] == "A8"]
A8_IDS = {row["id"] for row in A8}

X = sympy.Symbol("x", real=True)

BLOCKED = set(A8_IDS)


def _post(client: TestClient, path: str, payload: dict) -> dict:
    response = client.post(path, json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def test_edcx_fixture_a8_matches_the_frozen_source():
    assert len(ROWS) == 638
    assert len(A8) == 6
    assert BLOCKED == A8_IDS


def test_edcx_a8_no_solution_and_infinite_solutions_share_the_same_error():
    client = TestClient(app)
    none_body = _post(client, "/api/v1/ode", {"expression": "y'=y/x, y(0)=1"})
    many_body = _post(client, "/api/v1/ode", {"expression": "y'=y/x, y(0)=0"})

    # El canal no distingue los dos casos: mismo código y mismo mensaje.
    assert none_body["success"] is False and many_body["success"] is False
    assert none_body["error_code"] == many_body["error_code"] == "UNSUPPORTED_OPERATION"
    assert none_body["error_message"] == many_body["error_message"]

    # Oráculo: toda solución y=Cx cumple y(0)=0.
    c = sympy.Symbol("C")
    family = c * X
    assert sympy.simplify(sympy.diff(family, X) - family / X) == 0
    assert sympy.simplify(family.subs(X, 0)) == 0
    # Por tanto y(0)=1 no tiene solución y y(0)=0 tiene infinitas.
    assert sympy.solve(sympy.Eq(family.subs(X, 0), 1), c) == []


def test_edcx_a8_nonunique_row_does_not_return_the_two_branches():
    client = TestClient(app)
    body = _post(client, "/api/v1/ode", {"expression": "y'=sqrt(abs(y)), y(0)=0"})
    assert body["success"] is True
    # Devuelve una integral implícita, no y=0 e y=x|x|/4.
    assert "Integral" in body["result_text"]

    # Oráculo: y=0 y la rama y=x|x|/4 (x^2/4 si x>0, -x^2/4 si x<0) satisfacen
    # la EDO y la condición y(0)=0: la solución no es única.
    zero = sympy.Integer(0)
    assert sympy.simplify(sympy.diff(zero, X) - sympy.sqrt(sympy.Abs(zero))) == 0
    x_pos = sympy.Symbol("x_pos", positive=True)
    x_neg = sympy.Symbol("x_neg", negative=True)
    for symbol, branch in ((x_pos, x_pos**2 / 4), (x_neg, -x_neg**2 / 4)):
        assert branch.subs(symbol, 0) == 0
        assert sympy.simplify(sympy.diff(branch, symbol) - sympy.sqrt(sympy.Abs(branch))) == 0


def test_edcx_a8_maximal_interval_is_not_enforced_before_evaluating():
    client = TestClient(app)
    solution = _post(client, "/api/v1/ode", {"expression": "y'=y^2, y(0)=1"})
    assert solution["success"] is True

    evaluated = _post(
        client,
        "/api/v1/evaluate",
        {"expression": "1/(1-x)", "substitutions": {"x": "2"}},
    )
    # La fila exige un error claro fuera de (-infinito, 1); el canal devuelve -1.
    assert evaluated["success"] is True
    assert sympy.sympify(evaluated["result_text"]) == -1
    assert evaluated["error_code"] is None
    # Solo anota x != 1; no hay veredicto de intervalo máximo.
    kinds = {item["kind"] for item in evaluated["domain_conditions"]}
    assert "domain" in kinds

    # Oráculo: la solución tiene un polo en x=1 y no está definida en x=2.
    assert sympy.solve(sympy.denom(sympy.together(1 / (1 - X))), X) == [1]
    assert sympy.limit(1 / (1 - X), X, 1, "+") == -sympy.oo


def test_edcx_a8_singular_branch_is_not_completed():
    client = TestClient(app)
    body = _post(client, "/api/v1/ode", {"expression": "y'=x/y, y(0)=0"})
    assert body["success"] is True
    # Devuelve una sola rama, -sqrt(x^2) = -|x|; la fila pide y=+-x.
    assert "sqrt" in body["result_text"]
    assert "+-" not in body["result_text"]
    assert body["domain_conditions"] == []

    # Oráculo: y=+-x satisface y'=x/y para y != 0; la ecuación es singular en y=0.
    for branch in (X, -X):
        assert sympy.simplify(sympy.diff(branch, X) - X / branch) == 0
    # Ambas ramas coinciden solo en x=0: la solución no es única en el origen.
    assert sympy.solve(sympy.Eq(X, -X), X) == [0]


def test_edcx_a8_incompatible_boundary_problem_is_rejected_by_the_ic_limit():
    client = TestClient(app)
    body = _post(client, "/api/v1/ode", {"expression": "y''+y=0, y(0)=0, y(pi)=1"})
    assert body["success"] is False
    assert body["error_code"] == "PARSE_ERROR"
    assert "condici" in body["error_message"]

    # Oráculo: y=C1 cos x + C2 sin x; y(0)=0 -> C1=0; y(pi)=1 -> 0=1.
    c1, c2 = sympy.symbols("C1 C2")
    general = c1 * sympy.cos(X) + c2 * sympy.sin(X)
    c1_value = sympy.solve(sympy.Eq(general.subs(X, 0), 0), c1)[0]
    reduced = general.subs(c1, c1_value)
    assert sympy.simplify(reduced.subs(X, sympy.pi)) == 0
    assert sympy.solve(sympy.Eq(reduced.subs(X, sympy.pi), 1), c2) == []


def test_edcx_a8_classification_counts_are_explicit():
    assert len(A8) == 6
    assert len(BLOCKED) == 6
    assert BLOCKED == A8_IDS
