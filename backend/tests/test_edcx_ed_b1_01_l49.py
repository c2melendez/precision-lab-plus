"""EDCX Parte B — B1 "Conversión entre representaciones" (49 filas).

Canal
-----
El producto evalúa la forma binómica, la forma trigonométrica y la forma
exponencial cuando se escriben en sintaxis ASCII (`1+i`, `r*(cos(t)+i*sin(t))`,
`exp(i*t)`). No existe notación polar de entrada: `2_{pi/3}` devuelve
`PARSE_ERROR` y la palabra `angle` se interpreta como símbolo libre. Tampoco
existe un emisor de notación polar: `topolar(z)` colapsa a la forma binómica
(`topolar(3)=3`, `topolar(-2)=-2`) o a una raíz (`2*(-1)**(1/3)`).

Por eso la conversión se certifica con dos operaciones reales del producto,
`abs(z)` y `arg(z)`, y se comprueba con un oráculo sympy independiente que el
par `(r, theta)` reconstruye exactamente `z` en las tres formas:

    X: r*exp(i*theta) == z
    T: r*cos(theta) + i*r*sin(theta) == z
    B: re(z) + i*im(z) == z   (re/im también son operaciones reales)

Clasificación
-------------
- PASS_SCOPED (45): B-01..B-16, P-01..P-10, T-01..T-08, X-01..X-11. El
  contenido matemático de las tres representaciones es exacto; la notación
  `r_theta` se traduce a `r*(cos(theta)+i*sin(theta))` (filas P) y el par
  `(r, theta)` se lee de `abs`/`arg` (todas las filas). No se atribuye al
  producto ninguna forma que no emita.
- BLOCKED (4):
  * B-17 (`z=0`): `abs(0)=0` es correcto, pero `arg(0)=0` sin aviso, mientras
    que `topolar(0)` sí devuelve `DOMAIN_ERROR`; la fila exige argumento
    indefinido con aviso claro.
  * T-09, T-10, X-12 (theta simbólico): el producto devuelve `Abs(...)` y
    `arg(...)` sin reducir; no entrega las formas semángulo
    `2cos(theta/2)_{theta/2}`, `2sin(theta/2)_{(pi-theta)/2}` ni `1_{-theta}`.

Las identidades se comprueban con sympy; nunca se atribuyen al producto.
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
B1 = [row for row in ROWS if row["bloque"] == "B1"]
B1_IDS = {row["id"] for row in B1}

I = sympy.I  # noqa: E741 - unidad imaginaria, notación matemática estándar
PI = sympy.pi
THETA = sympy.Symbol("theta", real=True)

LOCALS = {
    "I": I,
    "pi": PI,
    "E": sympy.E,
    "exp": sympy.exp,
    "sqrt": sympy.sqrt,
    "cos": sympy.cos,
    "sin": sympy.sin,
    "atan": sympy.atan,
    "ln": sympy.log,
    "Abs": sympy.Abs,
    "arg": sympy.arg,
    "theta": THETA,
}

# Entrada normalizada al canal real. Las filas P traducen `r_theta` a la forma
# trigonométrica, que el producto sí acepta; el resto es sintaxis literal.
SOURCES = {
    "VC-CV-B-01": "1+i",
    "VC-CV-B-02": "1+i*sqrt(3)",
    "VC-CV-B-03": "-1+i",
    "VC-CV-B-04": "-1-i",
    "VC-CV-B-05": "1-i*sqrt(3)",
    "VC-CV-B-06": "-sqrt(3)+i",
    "VC-CV-B-07": "i",
    "VC-CV-B-08": "-i",
    "VC-CV-B-09": "-2",
    "VC-CV-B-10": "3",
    "VC-CV-B-11": "3+4*i",
    "VC-CV-B-12": "-3+4*i",
    "VC-CV-B-13": "5-12*i",
    "VC-CV-B-14": "-5-12*i",
    "VC-CV-B-15": "1/2-(sqrt(3)/2)*i",
    "VC-CV-B-16": "sqrt(2+sqrt(2))+i*sqrt(2-sqrt(2))",
    "VC-CV-B-17": "0",
    "VC-CV-P-01": "2*(cos(pi/3)+i*sin(pi/3))",
    "VC-CV-P-02": "4*(cos(pi/2)+i*sin(pi/2))",
    "VC-CV-P-03": "1*(cos(pi)+i*sin(pi))",
    "VC-CV-P-04": "6*(cos(5*pi/6)+i*sin(5*pi/6))",
    "VC-CV-P-05": "2*(cos(-pi/6)+i*sin(-pi/6))",
    "VC-CV-P-06": "3*(cos(7*pi/4)+i*sin(7*pi/4))",
    "VC-CV-P-07": "2*(cos(9*pi/4)+i*sin(9*pi/4))",
    "VC-CV-P-08": "5*(cos(60*pi/180)+i*sin(60*pi/180))",
    "VC-CV-P-09": "2*(cos(225*pi/180)+i*sin(225*pi/180))",
    "VC-CV-P-10": "-2*(cos(pi/3)+i*sin(pi/3))",
    "VC-CV-T-01": "2*(cos(pi/6)+i*sin(pi/6))",
    "VC-CV-T-02": "cos(pi/2)+i*sin(pi/2)",
    "VC-CV-T-03": "4*(cos(2*pi/3)+i*sin(2*pi/3))",
    "VC-CV-T-04": "3*(cos(210*pi/180)+i*sin(210*pi/180))",
    "VC-CV-T-05": "2*(cos(pi/5)+i*sin(pi/5))",
    "VC-CV-T-06": "-2*(cos(pi/6)+i*sin(pi/6))",
    "VC-CV-T-07": "2*(cos(pi/6)-i*sin(pi/6))",
    "VC-CV-T-08": "2*(sin(pi/3)+i*cos(pi/3))",
    "VC-CV-T-09": "1+cos(theta)+i*sin(theta)",
    "VC-CV-T-10": "1-cos(theta)+i*sin(theta)",
    "VC-CV-X-01": "exp(i*pi)",
    "VC-CV-X-02": "2*exp(i*pi/2)",
    "VC-CV-X-03": "exp(-i*pi/3)",
    "VC-CV-X-04": "3*exp(i*pi/4)",
    "VC-CV-X-05": "exp(1+i*pi)",
    "VC-CV-X-06": "exp(2+i)",
    "VC-CV-X-07": "exp(i)",
    "VC-CV-X-08": "exp(i*pi/3+2*pi*i)",
    "VC-CV-X-09": "2*exp(-5*i*pi/3)",
    "VC-CV-X-10": "exp(ln(2)+i*pi/3)",
    "VC-CV-X-11": "-exp(i*pi/6)",
    "VC-CV-X-12": "exp(-i*theta)",
}

# Oráculo independiente: (z exacto, módulo exacto, argumento principal).
ORACLE = {
    "VC-CV-B-01": (1 + I, sympy.sqrt(2), PI / 4),
    "VC-CV-B-02": (1 + I * sympy.sqrt(3), 2, PI / 3),
    "VC-CV-B-03": (-1 + I, sympy.sqrt(2), 3 * PI / 4),
    "VC-CV-B-04": (-1 - I, sympy.sqrt(2), -3 * PI / 4),
    "VC-CV-B-05": (1 - I * sympy.sqrt(3), 2, -PI / 3),
    "VC-CV-B-06": (-sympy.sqrt(3) + I, 2, 5 * PI / 6),
    "VC-CV-B-07": (I, 1, PI / 2),
    "VC-CV-B-08": (-I, 1, -PI / 2),
    "VC-CV-B-09": (-2, 2, PI),
    "VC-CV-B-10": (3, 3, 0),
    "VC-CV-B-11": (3 + 4 * I, 5, sympy.atan(sympy.Rational(4, 3))),
    "VC-CV-B-12": (-3 + 4 * I, 5, PI - sympy.atan(sympy.Rational(4, 3))),
    "VC-CV-B-13": (5 - 12 * I, 13, -sympy.atan(sympy.Rational(12, 5))),
    "VC-CV-B-14": (-5 - 12 * I, 13, sympy.atan(sympy.Rational(12, 5)) - PI),
    "VC-CV-B-15": (
        sympy.Rational(1, 2) - I * sympy.sqrt(3) / 2,
        1,
        -PI / 3,
    ),
    "VC-CV-B-16": (
        sympy.sqrt(2 + sympy.sqrt(2)) + I * sympy.sqrt(2 - sympy.sqrt(2)),
        2,
        PI / 8,
    ),
    "VC-CV-P-01": (1 + I * sympy.sqrt(3), 2, PI / 3),
    "VC-CV-P-02": (4 * I, 4, PI / 2),
    "VC-CV-P-03": (-1, 1, PI),
    "VC-CV-P-04": (-3 * sympy.sqrt(3) + 3 * I, 6, 5 * PI / 6),
    "VC-CV-P-05": (sympy.sqrt(3) - I, 2, -PI / 6),
    "VC-CV-P-06": (
        3 * sympy.sqrt(2) / 2 - I * 3 * sympy.sqrt(2) / 2,
        3,
        -PI / 4,
    ),
    "VC-CV-P-07": (sympy.sqrt(2) + I * sympy.sqrt(2), 2, PI / 4),
    "VC-CV-P-08": (
        sympy.Rational(5, 2) + I * 5 * sympy.sqrt(3) / 2,
        5,
        PI / 3,
    ),
    "VC-CV-P-09": (-sympy.sqrt(2) - I * sympy.sqrt(2), 2, -3 * PI / 4),
    "VC-CV-P-10": (-1 - I * sympy.sqrt(3), 2, -2 * PI / 3),
    "VC-CV-T-01": (sympy.sqrt(3) + I, 2, PI / 6),
    "VC-CV-T-02": (I, 1, PI / 2),
    "VC-CV-T-03": (-2 + 2 * I * sympy.sqrt(3), 4, 2 * PI / 3),
    "VC-CV-T-04": (
        -3 * sympy.sqrt(3) / 2 - I * sympy.Rational(3, 2),
        3,
        -5 * PI / 6,
    ),
    "VC-CV-T-05": (2 * sympy.exp(I * PI / 5), 2, PI / 5),
    "VC-CV-T-06": (-sympy.sqrt(3) - I, 2, -5 * PI / 6),
    "VC-CV-T-07": (sympy.sqrt(3) - I, 2, -PI / 6),
    "VC-CV-T-08": (sympy.sqrt(3) + I, 2, PI / 6),
    "VC-CV-X-01": (-1, 1, PI),
    "VC-CV-X-02": (2 * I, 2, PI / 2),
    "VC-CV-X-03": (sympy.Rational(1, 2) - I * sympy.sqrt(3) / 2, 1, -PI / 3),
    "VC-CV-X-04": (
        3 * sympy.sqrt(2) / 2 + I * 3 * sympy.sqrt(2) / 2,
        3,
        PI / 4,
    ),
    "VC-CV-X-05": (-sympy.E, sympy.E, PI),
    "VC-CV-X-06": (sympy.exp(2 + I), sympy.exp(2), 1),
    "VC-CV-X-07": (sympy.exp(I), 1, 1),
    "VC-CV-X-08": (sympy.Rational(1, 2) + I * sympy.sqrt(3) / 2, 1, PI / 3),
    "VC-CV-X-09": (1 + I * sympy.sqrt(3), 2, PI / 3),
    "VC-CV-X-10": (1 + I * sympy.sqrt(3), 2, PI / 3),
    "VC-CV-X-11": (
        -sympy.sqrt(3) / 2 - I * sympy.Rational(1, 2),
        1,
        -5 * PI / 6,
    ),
}

TRANSLATED = {row_id for row_id in B1_IDS if row_id.startswith("VC-CV-P-")}
BLOCKED = {"VC-CV-B-17", "VC-CV-T-09", "VC-CV-T-10", "VC-CV-X-12"}
PASS_SCOPED = B1_IDS - BLOCKED

# Notación polar literal de la fuente, rechazada por el canal.
RAW_POLAR = {
    "VC-CV-P-01": "2_{pi/3}",
    "VC-CV-P-02": "4_{pi/2}",
    "VC-CV-P-03": "1_{pi}",
    "VC-CV-P-04": "6_{5*pi/6}",
    "VC-CV-P-05": "2_{-pi/6}",
    "VC-CV-P-06": "3_{7*pi/4}",
    "VC-CV-P-07": "2_{9*pi/4}",
    "VC-CV-P-08": "5_{60}",
    "VC-CV-P-09": "2_{225}",
    "VC-CV-P-10": "(-2)_{pi/3}",
}


def _post(client: TestClient, path: str, payload: dict) -> dict:
    response = client.post(path, json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def _evaluate(client: TestClient, expression: str) -> dict:
    return _post(client, "/api/v1/evaluate", {"expression": expression})


def _result(client: TestClient, expression: str) -> str:
    body = _evaluate(client, expression)
    assert body["success"] is True, body
    return body["result_text"]


def _parse(text: str) -> sympy.Expr:
    return sympy.sympify(text, locals=LOCALS)


def _same(left, right) -> bool:
    """Igualdad exacta, o a 60 dígitos cuando la forma no se reduce."""
    delta = sympy.simplify(left - right)
    if delta == 0:
        return True
    try:
        return abs(complex(sympy.N(delta, 60))) < 1e-45
    except (TypeError, ValueError):
        return False


def _is_zero(expression) -> bool:
    """Identidad trigonométrica/compleja exacta (expande y simplifica)."""
    return sympy.simplify(sympy.expand(expression, complex=True)) == 0


def test_edcx_fixture_b1_matches_the_frozen_source():
    assert len(ROWS) == 638
    assert len(B1) == 49
    assert set(SOURCES) == B1_IDS
    assert set(ORACLE) | BLOCKED == B1_IDS
    assert PASS_SCOPED | BLOCKED == B1_IDS
    assert len(PASS_SCOPED) == 45 and len(BLOCKED) == 4
    assert TRANSLATED == {row_id for row_id in B1_IDS if row_id.startswith("VC-CV-P-")}
    assert set(RAW_POLAR) == TRANSLATED


@pytest.mark.parametrize("row_id", sorted(PASS_SCOPED))
def test_edcx_b1_polar_pair_reconstructs_the_three_forms(row_id):
    client = TestClient(app)
    z, modulus, argument = ORACLE[row_id]
    source = SOURCES[row_id]

    direct = _evaluate(client, source)
    assert direct["success"] is True
    assert _same(_parse(direct["result_text"]), z)

    real = _parse(_result(client, f"re({source})"))
    imag = _parse(_result(client, f"im({source})"))
    assert _same(real, sympy.re(z))
    assert _same(imag, sympy.im(z))

    r = _parse(_result(client, f"abs({source})"))
    theta = _parse(_result(client, f"arg({source})"))
    assert _same(r, modulus)
    assert _same(theta, argument)

    # Oráculo: el par (r, theta) del producto reconstruye z en las tres formas.
    assert _same(r * sympy.exp(I * theta), z)
    assert _same(r * sympy.cos(theta) + I * r * sympy.sin(theta), z)
    assert _same(real + I * imag, z)


@pytest.mark.parametrize("row_id", sorted(TRANSLATED))
def test_edcx_b1_p_rows_require_documented_notation_translation(row_id):
    client = TestClient(app)
    raw = _evaluate(client, RAW_POLAR[row_id])
    assert raw["success"] is False
    assert raw["error_code"] == "PARSE_ERROR"

    # La traducción documentada r_theta -> r*(cos(theta)+i*sin(theta)) sí evalúa.
    translated = _evaluate(client, SOURCES[row_id])
    assert translated["success"] is True
    assert _same(_parse(translated["result_text"]), ORACLE[row_id][0])


def test_edcx_b1_polar_notation_has_no_output_channel():
    client = TestClient(app)

    # topolar no emite r_theta: colapsa a binómica o a forma de raíz.
    assert _result(client, "topolar(3)") == "3"
    assert _result(client, "topolar(-2)") == "-2"
    root_form = _result(client, "topolar(1+i)")
    assert "exp(" not in root_form
    assert "(-1)**" in root_form and "sqrt(2)" in root_form
    assert _same(_parse(root_form), 1 + I)

    # El único endpoint "polar" grafica r=f(theta); no convierte un complejo
    # a notación polar.
    paths = app.openapi()["paths"]
    assert [path for path in paths if "polar" in path.lower()] == ["/api/v1/graph/polar"]
    schema = app.openapi()["components"]["schemas"]["GraphPolarRequest"]
    assert set(schema["properties"]) == {
        "r_expression",
        "variable",
        "theta_min",
        "theta_max",
    }

    # `angle` no se reconoce como operador: se multiplica como símbolo libre.
    angled = _evaluate(client, "2 angle pi/3")
    assert angled["success"] is True
    assert angled["result_text"] == "2*pi*angle/3"


def test_edcx_b1_zero_row_reports_a_defined_argument():
    client = TestClient(app)
    assert _result(client, "0") == "0"
    assert _result(client, "abs(0)") == "0"

    # Defecto: arg(0) devuelve 0 mientras que topolar(0) sí falla por dominio.
    assert _result(client, "arg(0)") == "0"
    polar = _evaluate(client, "topolar(0)")
    assert polar["success"] is False
    assert polar["error_code"] == "DOMAIN_ERROR"

    expected = next(row["esperado"] for row in B1 if row["id"] == "VC-CV-B-17")
    assert "indefinido" in expected


def test_edcx_b1_symbolic_half_angle_rows_are_not_reduced():
    client = TestClient(app)
    half = THETA / 2

    # T-09: 1 + e^{i theta} = 2 cos(theta/2) e^{i theta/2}.
    abs_09 = _result(client, f"abs({SOURCES['VC-CV-T-09']})")
    arg_09 = _result(client, f"arg({SOURCES['VC-CV-T-09']})")
    assert abs_09 == "Abs(exp(I*theta) + 1)"
    assert arg_09 == "arg(exp(I*theta) + 1)"
    assert _is_zero(1 + sympy.exp(I * THETA) - 2 * sympy.cos(half) * sympy.exp(I * half))

    # T-10: 1 - e^{-i theta} = 2 i sin(theta/2) e^{-i theta/2}.
    abs_10 = _result(client, f"abs({SOURCES['VC-CV-T-10']})")
    arg_10 = _result(client, f"arg({SOURCES['VC-CV-T-10']})")
    assert abs_10 == "Abs(1 - exp(-I*theta))"
    assert arg_10 == "arg(1 - exp(-I*theta))"
    assert _is_zero(1 - sympy.exp(-I * THETA) - 2 * I * sympy.sin(half) * sympy.exp(-I * half))

    # X-12: e^{-i theta} = cos(theta) - i sin(theta); |z| = 1, arg = -theta.
    abs_12 = _result(client, f"abs({SOURCES['VC-CV-X-12']})")
    arg_12 = _result(client, f"arg({SOURCES['VC-CV-X-12']})")
    assert abs_12 == "exp(im(theta))"
    assert arg_12 == "arg(exp(-I*theta))"
    assert _is_zero(sympy.exp(-I * THETA) - (sympy.cos(THETA) - I * sympy.sin(THETA)))


def test_edcx_b1_exact_argument_and_approximation_disagree_at_the_cut():
    client = TestClient(app)
    for source in ("exp(i*pi)", "exp(1+i*pi)"):
        body = _evaluate(client, f"arg({source})")
        assert body["success"] is True
        assert _same(_parse(body["result_text"]), PI)
        # Hallazgo: el canal exacto devuelve pi y el aproximado, -pi.
        assert body["result_approx"] is not None
        assert float(body["result_approx"]) < 0


def test_edcx_b1_classification_counts_are_explicit():
    assert len(B1) == 49
    assert len(PASS_SCOPED) == 45
    assert len(BLOCKED) == 4
    assert PASS_SCOPED | BLOCKED == B1_IDS
    assert BLOCKED == {
        "VC-CV-B-17",
        "VC-CV-T-09",
        "VC-CV-T-10",
        "VC-CV-X-12",
    }
