"""EDCX Parte A · A5 "Series y Frobenius" (10 filas).

Canal
-----
El motor EDO de Plus (`/api/v1/ode`) resuelve las ocho ecuaciones de este bloque
en forma cerrada, incluidas las que la fuente plantea por series: Airy (F-02),
Bessel (F-03/F-04/F-05) y las series de Legendre/Hermite/Chebyshev (F-06..F-08).
No hay una operación separada de "desarrollar en serie": cuando el producto
devuelve una serie, lo hace truncada (`O(x**6)`), y se certifica como
PASS_SCOPED comparando coeficientes con la forma cerrada de la fuente.

Clasificación
-------------
- PASS (5): F-01..F-05. Se devuelve la solución general; se verifica el residuo
  simbólico, que la familia tenga dos soluciones independientes (wronskiano no
  nulo) y que la forma cerrada de la fuente también satisfaga la EDO.
- PASS_SCOPED (3): F-06 devuelve una serie truncada que coincide con el
  desarrollo de la forma cerrada hasta el orden mostrado; F-07/F-08 devuelven la
  familia general y la solución polinomial de la fuente se obtiene fijando las
  constantes (elección documentada).
- BLOCKED (2): F-09/F-10 piden *clasificar* el punto x=0. El producto resuelve
  la EDO (Bessel) pero no emite ninguna clasificación y no existe endpoint ni
  operación de puntos singulares. La etiqueta esperada se verifica aquí con un
  oráculo independiente, nunca se atribuye al producto.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import sympy
from fastapi.testclient import TestClient

from app.main import app

ROOT = Path(__file__).resolve().parents[2]
SOURCE_GZ = ROOT / "qa/certification/legacy_sources/matriz_edo_variable_compleja.md.gz"
JSONL = ROOT / "qa/certification/edcx_ejecutables.jsonl"

ROWS = [json.loads(line) for line in JSONL.read_text(encoding="utf-8").splitlines() if line.strip()]
A5 = [row for row in ROWS if row["bloque"] == "A5"]

X = sympy.Symbol("x", positive=True)
Y = sympy.Function("y")
C1, C2 = sympy.symbols("C1 C2")
NU = sympy.Symbol("nu")

LOCALS = {
    "y": Y,
    "x": X,
    "airyai": sympy.airyai,
    "airybi": sympy.airybi,
    "besselj": sympy.besselj,
    "bessely": sympy.bessely,
    "O": sympy.O,
}

# Entrada normalizada al canal real (la fuente ya usa x como variable).
BACKEND_INPUT = {
    "ED-F-01": "y''+y=0",
    "ED-F-02": "y''-x*y=0",
    "ED-F-03": "2*x*y''+y'+y=0",
    "ED-F-04": "x^2*y''+x*y'+x^2*y=0",
    "ED-F-05": "x^2*y''+x*y'+(x^2-1/4)*y=0",
    "ED-F-06": "(1-x^2)*y''-2*x*y'+2*y=0",
    "ED-F-07": "y''-2*x*y'+4*y=0",
    "ED-F-08": "(1-x^2)*y''-x*y'+4*y=0",
    "ED-F-09": "x^2*y''+x*y'+(x^2-nu^2)*y=0",
    "ED-F-10": "x^3*y''+y=0",
}

EXACT = {
    "ED-F-01": sympy.Eq(sympy.diff(Y(X), X, 2) + Y(X), 0),
    "ED-F-02": sympy.Eq(sympy.diff(Y(X), X, 2) - X * Y(X), 0),
    "ED-F-03": sympy.Eq(2 * X * sympy.diff(Y(X), X, 2) + sympy.diff(Y(X), X) + Y(X), 0),
    "ED-F-04": sympy.Eq(
        X**2 * sympy.diff(Y(X), X, 2) + X * sympy.diff(Y(X), X) + X**2 * Y(X), 0
    ),
    "ED-F-05": sympy.Eq(
        X**2 * sympy.diff(Y(X), X, 2)
        + X * sympy.diff(Y(X), X)
        + (X**2 - sympy.Rational(1, 4)) * Y(X),
        0,
    ),
    "ED-F-06": sympy.Eq(
        (1 - X**2) * sympy.diff(Y(X), X, 2) - 2 * X * sympy.diff(Y(X), X) + 2 * Y(X), 0
    ),
    "ED-F-07": sympy.Eq(
        sympy.diff(Y(X), X, 2) - 2 * X * sympy.diff(Y(X), X) + 4 * Y(X), 0
    ),
    "ED-F-08": sympy.Eq(
        (1 - X**2) * sympy.diff(Y(X), X, 2) - X * sympy.diff(Y(X), X) + 4 * Y(X), 0
    ),
}

# Forma cerrada de la fuente (constantes renombradas a C1/C2 para comparar).
EXPECTED = {
    "ED-F-01": C1 * sympy.sin(X) + C2 * sympy.cos(X),
    "ED-F-02": C1 * sympy.airyai(X) + C2 * sympy.airybi(X),
    "ED-F-03": C1 * sympy.cos(sympy.sqrt(2 * X)) + C2 * sympy.sin(sympy.sqrt(2 * X)),
    "ED-F-04": C1 * sympy.besselj(0, X) + C2 * sympy.bessely(0, X),
    "ED-F-05": (C1 * sympy.sin(X) + C2 * sympy.cos(X)) / sympy.sqrt(X),
}

CLOSED_FORM = {"ED-F-01", "ED-F-02", "ED-F-03", "ED-F-04", "ED-F-05"}
SERIES_OR_PARTICULAR = {"ED-F-06", "ED-F-07", "ED-F-08"}
CLASSIFICATION = {"ED-F-09", "ED-F-10"}

# Solución polinomial de la fuente como elección de constantes de la familia.
POLYNOMIAL = {
    "ED-F-07": (sympy.Rational(-1, 2), X**2 - sympy.Rational(1, 2)),
    "ED-F-08": (sympy.Integer(-1), 2 * X**2 - 1),
}

# Oráculo independiente de la clasificación: (p(x), q(x), etiqueta).
# x=0 es regular si x*p y x^2*q son analíticas; irregular si x^2*q tiene polo.
SINGULAR_ORACLE = {
    "ED-F-09": (1 / X, (X**2 - NU**2) / X**2, "regular"),
    "ED-F-10": (sympy.Integer(0), 1 / X**3, "irregular"),
}


def frozen_source() -> str:
    import gzip

    return gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")


def _post(client: TestClient, expression: str) -> dict:
    response = client.post("/api/v1/ode", json={"expression": expression})
    assert response.status_code == 200, response.text
    return response.json()


def _solution(body: dict) -> sympy.Eq:
    parsed = sympy.sympify(body["result_text"], locals=LOCALS)
    assert isinstance(parsed, sympy.Eq)
    return parsed


def _residual(equation: sympy.Eq, rhs) -> sympy.Expr:
    replacements = {Y(X): rhs}
    for order in (1, 2):
        replacements[sympy.Derivative(Y(X), (X, order))] = sympy.diff(rhs, X, order)
    return sympy.simplify((equation.lhs - equation.rhs).subs(replacements).doit())


def _wronskian(rhs, point: int = 2) -> float:
    first = rhs.subs({C1: 1, C2: 0})
    second = rhs.subs({C1: 0, C2: 1})
    value = first * sympy.diff(second, X) - sympy.diff(first, X) * second
    return float(sympy.N(value.subs(X, point)))


def test_edcx_fixture_a5_matches_the_frozen_source():
    assert len(ROWS) == 638
    assert len(A5) == 10
    assert set(BACKEND_INPUT) == {row["id"] for row in A5}
    assert CLOSED_FORM | SERIES_OR_PARTICULAR | CLASSIFICATION == set(BACKEND_INPUT)
    assert not (CLOSED_FORM & SERIES_OR_PARTICULAR)
    assert not (CLOSED_FORM & CLASSIFICATION)
    assert not (SERIES_OR_PARTICULAR & CLASSIFICATION)
    source = frozen_source()
    for row in A5:
        assert f"| {row['id']} |" in source


@pytest.mark.parametrize("row", [r for r in A5 if r["id"] in CLOSED_FORM], ids=lambda r: r["id"])
def test_edcx_a5_closed_form_is_the_general_solution(row: dict):
    with TestClient(app) as client:
        body = _post(client, BACKEND_INPUT[row["id"]])
    assert body["success"] is True, body.get("error_message")
    assert body["operation"] == "ode"
    rhs = _solution(body).rhs
    assert not rhs.has(Y(X))
    assert not rhs.has(sympy.O), f"{row['id']} devolvió una serie, no la forma cerrada"
    assert _residual(EXACT[row["id"]], rhs) == 0, f"{row['id']}: la solución no satisface la EDO"
    assert _residual(EXACT[row["id"]], EXPECTED[row["id"]]) == 0
    assert abs(_wronskian(rhs)) > 1e-9, f"{row['id']}: familia degenerada"


def test_edcx_a5_legendre_series_matches_the_closed_form_coefficients():
    """ED-F-06: el producto devuelve la serie truncada; se comparan coeficientes."""
    expression = BACKEND_INPUT["ED-F-06"]
    with TestClient(app) as client:
        body = _post(client, expression)
    assert body["success"] is True, body.get("error_message")
    rhs = _solution(body).rhs
    assert rhs.has(sympy.O), f"se esperaba una serie truncada: {rhs}"
    polynomial = rhs.removeO()
    first = sympy.simplify(polynomial.subs({C1: 1, C2: 0}))
    second = sympy.simplify(polynomial.subs({C1: 0, C2: 1}))
    assert sympy.simplify(first - X) == 0
    closed_form = X / 2 * sympy.log((1 + X) / (1 - X)) - 1
    expected_series = sympy.series(closed_form, X, 0, 6).removeO()
    assert sympy.simplify(second + expected_series) == 0, f"{second} != {-expected_series}"
    assert _residual(EXACT["ED-F-06"], closed_form) == 0


@pytest.mark.parametrize("row", [r for r in A5 if r["id"] in POLYNOMIAL], ids=lambda r: r["id"])
def test_edcx_a5_polynomial_solution_is_in_the_returned_family(row: dict):
    with TestClient(app) as client:
        body = _post(client, BACKEND_INPUT[row["id"]])
    assert body["success"] is True, body.get("error_message")
    rhs = _solution(body).rhs
    assert rhs.has(sympy.O), f"se esperaba la familia en serie: {rhs}"
    constant, target = POLYNOMIAL[row["id"]]
    polynomial = rhs.removeO().subs({C1: 0, C2: constant})
    assert sympy.simplify(polynomial - target) == 0, f"{polynomial} != {target}"
    assert _residual(EXACT[row["id"]], target) == 0


@pytest.mark.parametrize("row", [r for r in A5 if r["id"] in CLASSIFICATION], ids=lambda r: r["id"])
def test_edcx_a5_singular_point_classification_has_no_product_channel(row: dict):
    with TestClient(app) as client:
        body = _post(client, BACKEND_INPUT[row["id"]])
        # Único canal con "singularities": devuelve localizaciones, no el tipo ODE.
        probe = client.post(
            "/api/v1/complex/singularities",
            json={"expression": "1/z" if row["id"] == "ED-F-09" else "1/z^3"},
        ).json()
    # El endpoint /openapi.json está deshabilitado en el producto; el esquema
    # interno de FastAPI sigue exponiendo las rutas reales.
    paths = app.openapi()["paths"]
    # El motor resuelve la EDO, pero la fila pide clasificar el punto, no resolver.
    assert body["success"] is True, body.get("error_message")
    text = (body.get("result_text") or "").lower()
    for label in ("regular", "irregular", "singular", "punto"):
        assert label not in text, f"{row['id']}: el producto emitió '{label}'"
    # El canal de singularidades complejas solo devuelve el conjunto de puntos.
    assert probe["success"] is True, probe
    assert probe["result_text"] == "{0}", probe
    assert "regular" not in probe["result_text"].lower()
    assert "irregular" not in probe["result_text"].lower()
    # No existe ninguna operación de clasificación regular/irregular.
    assert not any(
        "classif" in path or ("regular" in path and "singular" in path)
        for path in paths
    )
    assert not any(
        "singular" in key or "classif" in key for key in body.keys()
    )
    # Oráculo independiente: la etiqueta esperada es matemáticamente correcta.
    p, q, expected = SINGULAR_ORACLE[row["id"]]
    first = sympy.limit(X * p, X, 0)
    second = sympy.limit(X**2 * q, X, 0)
    finite = first.is_finite is not False and second.is_finite is not False
    if expected == "regular":
        assert finite, (row["id"], first, second)
    else:
        assert not finite, (row["id"], first, second)
