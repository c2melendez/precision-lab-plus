"""EDCX Parte B — B4 "Ecuaciones en C" (34 filas, VC-EC-01..34).

Canal
-----
`/api/v1/solve` resuelve ecuaciones polinomicas complejas con raices exactas
en `result_data` (lista de `{text, latex, is_complex}`). `/api/v1/solve/system`
resuelve el sistema lineal de VC-EC-22. Las ecuaciones trascendentes devuelven
las raices principales de cada familia; no hay enumeracion de la familia
completa. El operador `Log` de la matriz no existe: el nombre de logaritmo
natural es `ln`. `log(z)` devuelve un conjunto vacio sin error.

Clasificacion (medida con el producto en el SHA de este commit)
---------------------------------------------------------------
- PASS (14): conjuntos finitos exactos y completos, incluido VC-EC-22 por
  `/solve/system`.
- PASS_SCOPED (14): raices validas pero con alcance acotado: multiplicidad no
  reportada (03), forma cartesiana en lugar de exponencial (10), solo la raiz
  principal de una familia infinita (23-30, 32, 33), `asin`/`acos` sin
  simplificar (28, 29), conjunto vacio correcto de `tan(z)=i` (31) y notacion
  `ln` en lugar de `Log` (34).
- FAIL (4): el producto devuelve un subconjunto incorrecto o vacio aunque la
  solucion existe (16, 17, 18, 19). Se marcan como `xfail` estricto con la
  solucion completa esperada; no se corrige producto en este bloque.
- BLOCKED (2): `abs(z)` no es resoluble (20, 21), `UNSUPPORTED_OPERATION`.

Los conjuntos y las identidades se comprueban con oraculos sympy
independientes; nunca se atribuyen al producto.
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
B4 = [row for row in ROWS if row["bloque"] == "B4"]
B4_IDS = {row["id"] for row in B4}

I = sympy.I  # noqa: E741 - unidad imaginaria, notacion matematica estandar
PI = sympy.pi
SQ3 = sympy.sqrt(3)
HALF = sympy.Rational(1, 2)

LOCALS = {
    "I": I,
    "pi": PI,
    "exp": sympy.exp,
    "sqrt": sympy.sqrt,
    "cos": sympy.cos,
    "sin": sympy.sin,
    "log": sympy.log,
    "ln": sympy.log,
    "asin": sympy.asin,
    "acos": sympy.acos,
    "E": sympy.E,
}


def _conj(value):
    return sympy.conjugate(value)


# Residuo f(z) de cada ecuacion, escrito directamente (sin parsear).
RESIDUAL = {
    "VC-EC-01": lambda v: v**2 + 1,
    "VC-EC-02": lambda v: v**2 + 2 * v + 5,
    "VC-EC-03": lambda v: v**2 - 2 * I * v - 1,
    "VC-EC-04": lambda v: v**2 - (3 + I) * v + (2 + I),
    "VC-EC-05": lambda v: v**2 + (1 - 2 * I) * v - 2 * I,
    "VC-EC-06": lambda v: v**2 - (3 + 4 * I),
    "VC-EC-07": lambda v: v**2 - (-5 + 12 * I),
    "VC-EC-08": lambda v: v**3 - 1,
    "VC-EC-09": lambda v: v**4 + 4,
    "VC-EC-10": lambda v: v**6 - 64,
    "VC-EC-11": lambda v: v**3 + v**2 + v + 1,
    "VC-EC-12": lambda v: v**4 + v**2 + 1,
    "VC-EC-13": lambda v: v**3 - 3 * v**2 + 3 * v - 2,
    "VC-EC-14": lambda v: (1 + I) * v - (2 - I),
    "VC-EC-15": lambda v: (v - I) - 2 * (v + I),
    "VC-EC-16": lambda v: v**2 + _conj(v),
    "VC-EC-17": lambda v: v**2 - _conj(v),
    "VC-EC-18": lambda v: v**3 - _conj(v),
    "VC-EC-19": lambda v: v * _conj(v) + 2 * v - (3 + 2 * I),
    "VC-EC-23": lambda v: sympy.exp(v) - 1,
    "VC-EC-24": lambda v: sympy.exp(v) + 1,
    "VC-EC-25": lambda v: sympy.exp(v) - (1 + I),
    "VC-EC-26": lambda v: sympy.exp(2 * v) - 3 * sympy.exp(v) + 2,
    "VC-EC-27": lambda v: sympy.sin(v),
    "VC-EC-28": lambda v: sympy.sin(v) - 2,
    "VC-EC-29": lambda v: sympy.cos(v) - 2,
    "VC-EC-30": lambda v: sympy.sin(v) - I,
    "VC-EC-31": lambda v: sympy.tan(v) - I,
    "VC-EC-32": lambda v: sympy.cosh(v),
    "VC-EC-33": lambda v: sympy.cosh(v) - 2,
}

EQUATION = {
    "VC-EC-01": "z^2+1=0",
    "VC-EC-02": "z^2+2*z+5=0",
    "VC-EC-03": "z^2-2*i*z-1=0",
    "VC-EC-04": "z^2-(3+i)*z+(2+i)=0",
    "VC-EC-05": "z^2+(1-2*i)*z-2*i=0",
    "VC-EC-06": "z^2=3+4*i",
    "VC-EC-07": "z^2=-5+12*i",
    "VC-EC-08": "z^3=1",
    "VC-EC-09": "z^4+4=0",
    "VC-EC-10": "z^6=64",
    "VC-EC-11": "z^3+z^2+z+1=0",
    "VC-EC-12": "z^4+z^2+1=0",
    "VC-EC-13": "z^3-3*z^2+3*z-2=0",
    "VC-EC-14": "(1+i)*z=2-i",
    "VC-EC-15": "(z-i)/(z+i)=2",
    "VC-EC-16": "z^2+conj(z)=0",
    "VC-EC-17": "z^2=conj(z)",
    "VC-EC-18": "z^3=conj(z)",
    "VC-EC-19": "z*conj(z)+2*z=3+2*i",
    "VC-EC-20": "abs(z)-z=1+2*i",
    "VC-EC-21": "abs(z)=z^2",
    "VC-EC-23": "exp(z)=1",
    "VC-EC-24": "exp(z)=-1",
    "VC-EC-25": "exp(z)=1+i",
    "VC-EC-26": "exp(2*z)-3*exp(z)+2=0",
    "VC-EC-27": "sin(z)=0",
    "VC-EC-28": "sin(z)=2",
    "VC-EC-29": "cos(z)=2",
    "VC-EC-30": "sin(z)=i",
    "VC-EC-31": "tan(z)=i",
    "VC-EC-32": "cosh(z)=0",
    "VC-EC-33": "cosh(z)=2",
    "VC-EC-34": "ln(z)=1+i*pi/2",
}

# Conjuntos finitos completos del enunciado (oraculo independiente).
EXACT = {
    "VC-EC-01": [I, -I],
    "VC-EC-02": [-1 + 2 * I, -1 - 2 * I],
    "VC-EC-04": [1, 2 + I],
    "VC-EC-05": [2 * I, -1],
    "VC-EC-06": [2 + I, -(2 + I)],
    "VC-EC-07": [2 + 3 * I, -(2 + 3 * I)],
    "VC-EC-08": [1, -HALF + SQ3 / 2 * I, -HALF - SQ3 / 2 * I],
    "VC-EC-09": [1 + I, 1 - I, -1 + I, -1 - I],
    "VC-EC-11": [-1, I, -I],
    "VC-EC-12": [HALF + SQ3 / 2 * I, HALF - SQ3 / 2 * I, -HALF + SQ3 / 2 * I, -HALF - SQ3 / 2 * I],
    "VC-EC-13": [2, HALF + SQ3 / 2 * I, HALF - SQ3 / 2 * I],
    "VC-EC-14": [HALF - sympy.Rational(3, 2) * I],
    "VC-EC-15": [-3 * I],
}

# Subconjunto del matriz completo; el producto devuelve menos raices.
EXPECTED_FULL = {
    "VC-EC-03": [I],
    "VC-EC-10": [2 * sympy.exp(I * PI * k / 3) for k in range(6)],
    "VC-EC-16": [0, -1, HALF + SQ3 / 2 * I, HALF - SQ3 / 2 * I],
    "VC-EC-17": [0, 1, -HALF + SQ3 / 2 * I, -HALF - SQ3 / 2 * I],
    "VC-EC-18": [0, 1, -1, I, -I],
    "VC-EC-19": [-1 + SQ3 + I, -1 - SQ3 + I],
}

PASS = set(EXACT) | {"VC-EC-22"}
PASS_SCOPED = {
    "VC-EC-03",
    "VC-EC-10",
    "VC-EC-23",
    "VC-EC-24",
    "VC-EC-25",
    "VC-EC-26",
    "VC-EC-27",
    "VC-EC-28",
    "VC-EC-29",
    "VC-EC-30",
    "VC-EC-31",
    "VC-EC-32",
    "VC-EC-33",
    "VC-EC-34",
}
FAIL = {"VC-EC-16", "VC-EC-17", "VC-EC-18", "VC-EC-19"}
BLOCKED = {"VC-EC-20", "VC-EC-21"}


def _post(client: TestClient, path: str, payload: dict) -> dict:
    response = client.post(path, json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def _solutions(client: TestClient, equation: str) -> list[sympy.Expr]:
    body = _post(client, "/api/v1/solve", {"equation": equation, "variable": "z"})
    assert body["success"] is True, body
    return [sympy.sympify(item["text"], locals=LOCALS) for item in body["result_data"]]


def _same(left, right) -> bool:
    delta = sympy.simplify(left - right)
    if delta == 0:
        return True
    try:
        return abs(complex(sympy.N(delta, 60))) < 1e-45
    except (TypeError, ValueError):
        return False


def _same_set(actual, expected) -> bool:
    if len(actual) != len(expected):
        return False
    remaining = list(expected)
    for value in actual:
        for index, candidate in enumerate(remaining):
            if _same(value, candidate):
                remaining.pop(index)
                break
        else:
            return False
    return not remaining


def _residual_ok(row_id: str, root) -> bool:
    value = complex(sympy.N(RESIDUAL[row_id](root), 40))
    return abs(value) < 1e-25


def test_edcx_fixture_b4_matches_the_frozen_source():
    assert len(ROWS) == 638
    assert len(B4) == 34
    assert B4_IDS == {f"VC-EC-{n:02d}" for n in range(1, 35)}
    assert PASS | PASS_SCOPED | FAIL | BLOCKED == B4_IDS
    assert not (PASS & PASS_SCOPED or PASS & FAIL or PASS & BLOCKED)
    assert not (PASS_SCOPED & FAIL or PASS_SCOPED & BLOCKED or FAIL & BLOCKED)
    assert len(PASS) == 14 and len(PASS_SCOPED) == 14
    assert len(FAIL) == 4 and len(BLOCKED) == 2


@pytest.mark.parametrize("row_id", sorted(EXACT))
def test_edcx_b4_finite_rows_return_the_exact_complete_set(row_id):
    client = TestClient(app)
    roots = _solutions(client, EQUATION[row_id])
    assert _same_set(roots, EXACT[row_id]), (row_id, roots)


def test_edcx_b4_system_row_returns_the_exact_pair():
    client = TestClient(app)
    body = _post(
        client,
        "/api/v1/solve/system",
        {"equations": ["z1+z2=1+i", "z1-z2=1-i"], "variables": ["z1", "z2"]},
    )
    assert body["success"] is True, body
    text = body["result_data"][0]["text"]
    assert text == "z1=1, z2=I"


@pytest.mark.parametrize("row_id", sorted(PASS_SCOPED - {"VC-EC-31", "VC-EC-34"}))
def test_edcx_b4_scoped_rows_return_valid_roots(row_id):
    client = TestClient(app)
    roots = _solutions(client, EQUATION[row_id])
    assert roots, row_id
    for root in roots:
        assert _residual_ok(row_id, root), (row_id, root)


def test_edcx_b4_scoped_cubic_row_is_complete_for_the_sextic_roots():
    # VC-EC-10: seis raices validas; forma cartesiana, no 2*e^(i*pi*k/3).
    client = TestClient(app)
    roots = _solutions(client, EQUATION["VC-EC-10"])
    assert len(roots) == 6
    assert _same_set(roots, EXPECTED_FULL["VC-EC-10"])


def test_edcx_b4_tan_equals_i_has_no_solution_in_the_complex_plane():
    # VC-EC-31: tan(z) omite +-i en C; el conjunto vacio es el correcto.
    client = TestClient(app)
    assert _solutions(client, EQUATION["VC-EC-31"]) == []


def test_edcx_b4_log_row_uses_ln_notation():
    client = TestClient(app)
    # VC-EC-34: Log z no existe; ln z = 1+i*pi/2 devuelve i*e.
    roots = _solutions(client, EQUATION["VC-EC-34"])
    assert _same_set(roots, [sympy.I * sympy.E])
    # log(z) con el mismo enunciado no falla: devuelve vacio sin error.
    body = _post(client, "/api/v1/solve", {"equation": "log(z)=1+i*pi/2", "variable": "z"})
    assert body["success"] is True
    assert body["result_data"] == []


@pytest.mark.parametrize("row_id", sorted(FAIL))
@pytest.mark.xfail(strict=True, reason="B4 FAIL: /solve devuelve un subconjunto incorrecto o vacio")
def test_edcx_b4_fail_rows_expose_the_missing_roots(row_id):
    client = TestClient(app)
    roots = _solutions(client, EQUATION[row_id])
    assert _same_set(roots, EXPECTED_FULL[row_id]), (row_id, roots)


@pytest.mark.parametrize("row_id", sorted(BLOCKED))
def test_edcx_b4_blocked_absolute_value_is_unsupported(row_id):
    client = TestClient(app)
    body = _post(client, "/api/v1/solve", {"equation": EQUATION[row_id], "variable": "z"})
    assert body["success"] is False
    assert body["error_code"] == "UNSUPPORTED_OPERATION"


def test_edcx_b4_classification_counts_are_explicit():
    assert PASS | PASS_SCOPED | FAIL | BLOCKED == B4_IDS
    assert len(PASS) == 14
    assert len(PASS_SCOPED) == 14
    assert len(FAIL) == 4
    assert len(BLOCKED) == 2
