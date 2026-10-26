"""EDCX Parte A — A6 "Ecuaciones en derivadas parciales" (26 filas).

Canal
-----
Plus no tiene motor de EDP: no existe endpoint de resolución de EDP,
clasificación de EDP, características, separación de variables, series de
Fourier ni núcleo del calor.  El único canal que toca derivadas multivariables
es ``/api/v1/derivative/partial`` (derivada parcial de orden 1..3 respecto de
*una* variable).

Clasificación
-------------
- PASS_SCOPED (1): ED-P-25 (`Δ(e^x sin y)`).  No hay endpoint "laplaciano";
  el arnés compone la definición `Δu = u_xx + u_yy` con dos llamadas reales a
  ``/api/v1/derivative/partial`` y suma ambos resultados por
  ``/api/v1/evaluate``.  El producto ejecuta las dos derivadas exactas y la
  suma da exactamente 0.  El alcance (composición, no botón dedicado) queda
  documentado.
- BLOCKED (25): el resto.  Los enunciados son EDP, problemas de valores
  iniciales/frontera, clasificación o el núcleo del calor.  Se mide el rechazo
  real de los canales existentes (``/api/v1/evaluate`` rechaza ecuaciones;
  ``/api/v1/ode`` rechaza más de una condición inicial) y la ausencia de rutas
  de EDP en el inventario de la aplicación.  Las respuestas de la fuente se
  comprueban con oráculos sympy independientes, pero nunca se atribuyen al
  producto.

Nota de medición
----------------
``y''+lambda*y=0`` sin condición dispara el solver EDO con parámetro no
soportado y agota el timeout (~3 s).  Por eso la evidencia de bloqueo de
P-23/P-24 usa el rechazo determinista de dos condiciones iniciales, no el
timeout.
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
A6 = [row for row in ROWS if row["bloque"] == "A6"]
A6_IDS = {row["id"] for row in A6}

# --- ED-P-25: laplaciano compuesto por derivadas parciales reales -----------
LAPLACIAN_ID = "ED-P-25"
LAPLACIAN_EXPRESSION = "e^x*sin(y)"
LAPLACIAN_WRT_X = "exp(x)*sin(y)"
LAPLACIAN_WRT_Y = "-exp(x)*sin(y)"

# --- Filas bloqueadas: sonda mínima enviada al canal que se mide ------------
# "evaluate" => el enunciado es una EDP/ecuación y el canal sólo evalúa
# expresiones.  "ode" => problema de autovalores con dos condiciones.
PROBE = {
    "ED-P-01": ("evaluate", "u_x+u_y=0"),
    "ED-P-02": ("evaluate", "u_x+2*u_y=0"),
    "ED-P-03": ("evaluate", "u_x+u_y=u"),
    "ED-P-04": ("evaluate", "x*u_x+y*u_y=u"),
    "ED-P-05": ("evaluate", "u_t+c*u_x=0"),
    "ED-P-06": ("evaluate", "u_t+u*u_x=0"),
    "ED-P-07": ("evaluate", "u_xy=0"),
    "ED-P-08": ("evaluate", "u_xy=x+y"),
    "ED-P-09": ("evaluate", "u_xx+u_yy=0"),
    "ED-P-10": ("evaluate", "x*u_xx+u_yy=0"),
    "ED-P-11": ("evaluate", "u_tt=c^2*u_xx"),
    "ED-P-12": ("evaluate", "u_tt=u_xx"),
    "ED-P-13": ("evaluate", "u_tt=u_xx"),
    "ED-P-14": ("evaluate", "u_tt=u_xx"),
    "ED-P-15": ("evaluate", "u_t=u_xx"),
    "ED-P-16": ("evaluate", "u_t=u_xx"),
    "ED-P-17": ("evaluate", "u_t=u_xx"),
    "ED-P-18": ("evaluate", "u_t=u_xx"),
    "ED-P-19": ("evaluate", "u_xx+u_yy=0"),
    "ED-P-20": ("evaluate", "u_xx+u_yy=0"),
    "ED-P-21": ("evaluate", "u_xx+u_yy=0"),
    "ED-P-22": ("evaluate", "u_xx+u_yy=4"),
    "ED-P-23": ("ode", "y''+lambda*y=0, y'(0)=0, y'(L)=0"),
    "ED-P-24": ("ode", "y''+lambda*y=0, y(0)=0, y'(L)=0"),
    "ED-P-26": ("evaluate", "u_t=u_xx"),
}

PASS_SCOPED = {LAPLACIAN_ID}


def _post(client: TestClient, path: str, payload: dict) -> dict:
    response = client.post(path, json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def test_edcx_fixture_a6_matches_the_frozen_source():
    assert len(ROWS) == 638
    assert len(A6) == 26
    assert set(PROBE) == A6_IDS - PASS_SCOPED
    assert len(PROBE) + len(PASS_SCOPED) == len(A6)


def test_edcx_a6_laplacian_is_composed_from_real_partial_derivatives():
    client = TestClient(app)

    dx = _post(
        client,
        "/api/v1/derivative/partial",
        {"expression": LAPLACIAN_EXPRESSION, "variable": "x", "order": 2},
    )
    dy = _post(
        client,
        "/api/v1/derivative/partial",
        {"expression": LAPLACIAN_EXPRESSION, "variable": "y", "order": 2},
    )
    assert dx["success"] is True and dy["success"] is True
    assert sympy.simplify(sympy.sympify(dx["result_text"]) - sympy.sympify(LAPLACIAN_WRT_X)) == 0
    assert sympy.simplify(sympy.sympify(dy["result_text"]) - sympy.sympify(LAPLACIAN_WRT_Y)) == 0

    total = _post(
        client,
        "/api/v1/evaluate",
        {"expression": f"({dx['result_text']})+({dy['result_text']})"},
    )
    assert total["success"] is True
    assert sympy.sympify(total["result_text"]) == 0

    # Oráculo independiente: el laplaciano de e^x sen y es idénticamente 0.
    x, y = sympy.symbols("x y")
    oracle = sympy.diff(sympy.exp(x) * sympy.sin(y), x, 2) + sympy.diff(
        sympy.exp(x) * sympy.sin(y), y, 2
    )
    assert sympy.simplify(oracle) == 0


@pytest.mark.parametrize("row_id", sorted(PROBE))
def test_edcx_a6_blocked_rows_are_rejected_by_every_existing_channel(row_id):
    channel, probe = PROBE[row_id]
    client = TestClient(app)
    if channel == "evaluate":
        body = _post(client, "/api/v1/evaluate", {"expression": probe})
        assert body["success"] is False
        assert body["error_code"] == "PARSE_ERROR"
        # El canal sólo evalúa expresiones; una EDP con "=" no es expresable.
        assert "No se esperaba" in body["error_message"]
    else:
        body = _post(client, "/api/v1/ode", {"expression": probe})
        assert body["success"] is False
        assert body["error_code"] == "PARSE_ERROR"
        assert "condici" in body["error_message"]


def test_edcx_a6_no_pde_route_exists_in_the_application():
    paths = app.openapi()["paths"]
    forbidden = ("pde", "classif", "characteristic", "heat", "wave", "fourier", "laplac")
    hits = sorted(
        path for path in paths if any(token in path.lower() for token in forbidden)
    )
    assert hits == []
    # El único canal multivariable es la derivada parcial de una variable.
    assert "/api/v1/derivative/partial" in paths


def test_edcx_a6_expected_answers_hold_under_an_independent_oracle():
    x, y = sympy.symbols("x y")
    f = sympy.Function("f")

    # P-01: u=f(x-y) satisface u_x+u_y=0 (regla de la cadena).
    u = f(x - y)
    assert sympy.simplify(sympy.diff(u, x) + sympy.diff(u, y)) == 0

    # P-12: u=sin x cos t satisface u_tt=u_xx y las dos condiciones.
    t = sympy.Symbol("t")
    u12 = sympy.sin(x) * sympy.cos(t)
    assert sympy.simplify(sympy.diff(u12, t, 2) - sympy.diff(u12, x, 2)) == 0
    assert sympy.simplify(u12.subs(t, 0) - sympy.sin(x)) == 0
    assert sympy.simplify(sympy.diff(u12, t).subs(t, 0)) == 0

    # P-15: u=e^{-9t} sin 3x satisface u_t=u_xx y las condiciones de frontera.
    u15 = sympy.exp(-9 * t) * sympy.sin(3 * x)
    assert sympy.simplify(sympy.diff(u15, t) - sympy.diff(u15, x, 2)) == 0
    assert sympy.simplify(u15.subs(x, 0)) == 0
    assert sympy.simplify(u15.subs(x, sympy.pi)) == 0
    assert sympy.simplify(u15.subs(t, 0) - sympy.sin(3 * x)) == 0

    # P-20: u=r^2 cos 2θ es armónica en el disco y cumple la traza.
    r, theta = sympy.symbols("r theta", positive=True)
    u20 = r**2 * sympy.cos(2 * theta)
    laplace20 = (
        sympy.diff(r * sympy.diff(u20, r), r) / r
        + sympy.diff(u20, theta, 2) / r**2
    )
    assert sympy.simplify(laplace20) == 0
    assert sympy.simplify(u20.subs(r, 1) - sympy.cos(2 * theta)) == 0


def test_edcx_a6_classification_counts_are_explicit():
    assert len(A6) == 26
    assert len(PASS_SCOPED) == 1
    assert len(PROBE) == 25
    assert PASS_SCOPED | set(PROBE) == A6_IDS
