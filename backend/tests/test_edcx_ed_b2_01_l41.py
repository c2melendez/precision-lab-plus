"""EDCX Parte B — B2 "Operaciones con números complejos" (41 filas).

Canal
-----
El producto evalúa una expresión ASCII con la unidad `i` y las funciones
`re`, `im`, `conj`, `abs`, `exp`, `cos`, `sin`, `sqrt`. La forma binómica se
introduce de forma literal, incluida la multiplicación implícita:
`(2+3i)(1-i)` devuelve `5 + I`. No existe notación polar de entrada: las
nueve formas `r_{\\theta}` de las filas P devuelven `PARSE_ERROR`, igual que
en B1, y la forma de papel `cos3theta` se interpreta como un símbolo libre
(`cos3theta`), no como `cos(3*theta)`.

La normalización LaTeX/Unicode y la multiplicación implícita a `*` son
sintácticas y no cambian la clasificación. La notación polar `r_{\\theta}` sí
carece de forma ASCII equivalente: se traduce a
`r*(cos(theta)+i*sin(theta))` y por eso las filas P se certifican como
PASS_SCOPED.

Clasificación
-------------
- PASS (20): B-01..B-11, T-01..T-03, X-01..X-03, X-05..X-07. Una sola
  operación devuelve exactamente el valor congelado.
- PASS_SCOPED (13):
  * P-01..P-09: la entrada polar se traduce a forma trigonométrica; el
    resultado es exacto, pero se emite en forma binómica o de raíz, no en
    notación `r_{\\theta}`.
  * T-05: el producto se devuelve como `exp(I*(alpha+beta))`, equivalente
    exacto por Euler de `cos(alpha+beta)+i*sin(alpha+beta)`.
  * X-04: se devuelve la potencia principal `32*(-1)**(5/6)`, que es
    exactamente `-16*sqrt(3)+16i`, en forma de raíz.
  * X-08: se devuelve `3*exp(-I*conjugate(theta))` (y
    `exp(-I*conjugate(theta))*conjugate(r)`); es exacto para `theta` y `r`
    reales, como en el ejercicio.
  * X-09: `abs(exp(a+b*i))` devuelve `exp(re(a) - im(b))`; con `a,b` reales
    (`re(a)=a`, `im(b)=0`) es exactamente `exp(a)`.
- BLOCKED (8):
  * T-04, X-10: la potencia de la forma exponencial no se combina; se
    devuelve `exp(I*theta)**n` sin producir `exp(I*n*theta)` ni
    `cos(n*theta)+i*sin(n*theta)`.
  * T-06, T-07, T-08: no hay expansión de ángulo múltiple ni linealización;
    la entrada se devuelve sin transformar.
  * T-09: no existe nodo de sumatoria; `sum(...)` y `Sum(...)` devuelven
    `PARSE_ERROR`.
  * X-11, X-12: no hay reescritura de media ángulo ni de serie geométrica;
    `1/(1-exp(I*theta))` y `Abs(exp(I*theta)+1)` se devuelven sin reducir.

Las identidades matemáticas de las filas BLOCKED y de las traducciones se
comprueban con oráculos sympy independientes; nunca se atribuyen al producto.
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
B2 = [row for row in ROWS if row["bloque"] == "B2"]
B2_IDS = {row["id"] for row in B2}

I = sympy.I  # noqa: E741 - unidad imaginaria, notación matemática estándar
PI = sympy.pi
THETA = sympy.Symbol("theta", real=True)
ALPHA = sympy.Symbol("alpha", real=True)
BETA = sympy.Symbol("beta", real=True)
REAL_R = sympy.Symbol("r", real=True)
REAL_A = sympy.Symbol("a", real=True)
REAL_B = sympy.Symbol("b", real=True)
N = sympy.Symbol("n", integer=True, positive=True)
K = sympy.Symbol("k", integer=True)

LOCALS = {
    "I": I,
    "pi": PI,
    "E": sympy.E,
    "exp": sympy.exp,
    "sqrt": sympy.sqrt,
    "cos": sympy.cos,
    "sin": sympy.sin,
    "cot": sympy.cot,
    "conjugate": sympy.conjugate,
    "re": sympy.re,
    "im": sympy.im,
    "Abs": sympy.Abs,
    "theta": THETA,
    "alpha": ALPHA,
    "beta": BETA,
    "r": REAL_R,
    "a": REAL_A,
    "b": REAL_B,
    "n": N,
    "k": K,
}

# Entrada ASCII mínima. Las filas P traducen `r_theta` a la forma
# trigonométrica, que el producto sí acepta; el resto es sintaxis literal.
SOURCES = {
    "VC-OP-B-01": ("(2+3i)+(1-i)",),
    "VC-OP-B-02": ("(2+3i)-(1-i)",),
    "VC-OP-B-03": ("(2+3i)(1-i)",),
    "VC-OP-B-04": ("(3+4i)/(1-2i)",),
    "VC-OP-B-05": ("(2+i)^2/(3-4i)",),
    "VC-OP-B-06": ("i^2026",),
    "VC-OP-B-07": ("(1+i)^10",),
    "VC-OP-B-08": ("(1+i)/(1-i)",),
    "VC-OP-B-09": ("conj(3-4i)", "abs(3-4i)"),
    "VC-OP-B-10": ("re(1/(1+i))", "im(1/(1+i))"),
    "VC-OP-B-11": ("1/i+1/(1+i)",),
    "VC-OP-P-01": ("2*(cos(pi/6)+i*sin(pi/6))*3*(cos(pi/3)+i*sin(pi/3))",),
    "VC-OP-P-02": ("8*(cos(pi)+i*sin(pi))/(2*(cos(pi/2)+i*sin(pi/2)))",),
    "VC-OP-P-03": ("(2*(cos(pi/6)+i*sin(pi/6)))^3",),
    "VC-OP-P-04": ("(sqrt(2)*(cos(pi/4)+i*sin(pi/4)))^4",),
    "VC-OP-P-05": ("1/(2*(cos(pi/3)+i*sin(pi/3)))",),
    "VC-OP-P-06": ("conj(3*(cos(pi/5)+i*sin(pi/5)))",),
    "VC-OP-P-07": (
        "2*(cos(3*pi/4)+i*sin(3*pi/4))*3*(cos(3*pi/4)+i*sin(3*pi/4))",
    ),
    "VC-OP-P-08": ("(1*(cos(pi/3)+i*sin(pi/3)))^6",),
    "VC-OP-P-09": ("(2*(cos(-pi/4)+i*sin(-pi/4)))^8",),
    "VC-OP-T-01": ("(cos(pi/12)+i*sin(pi/12))^6",),
    "VC-OP-T-02": ("(2*(cos(15*pi/180)+i*sin(15*pi/180)))^4",),
    "VC-OP-T-03": ("(cos(2*pi/3)+i*sin(2*pi/3))/(cos(pi/6)+i*sin(pi/6))",),
    "VC-OP-T-04": ("(cos(theta)+i*sin(theta))^n",),
    "VC-OP-T-05": ("(cos(alpha)+i*sin(alpha))*(cos(beta)+i*sin(beta))",),
    "VC-OP-T-06": ("cos(3*theta)",),
    "VC-OP-T-07": ("sin(3*theta)",),
    "VC-OP-T-08": ("cos(theta)^4",),
    "VC-OP-T-09": ("sum(cos(k*theta), k, 0, n)", "Sum(cos(k*theta), (k, 0, n))"),
    "VC-OP-X-01": ("exp(i*pi/3)*exp(i*pi/6)",),
    "VC-OP-X-02": ("exp(i*pi)/exp(-i*pi/2)",),
    "VC-OP-X-03": ("(exp(i*pi/4))^8",),
    "VC-OP-X-04": ("(2*exp(i*pi/6))^5",),
    "VC-OP-X-05": ("exp(i*theta)+exp(-i*theta)",),
    "VC-OP-X-06": ("exp(i*theta)-exp(-i*theta)",),
    "VC-OP-X-07": ("exp(i*pi)+1",),
    "VC-OP-X-08": ("conj(3*exp(i*theta))", "conj(r*exp(i*theta))"),
    "VC-OP-X-09": ("abs(exp(a+b*i))",),
    "VC-OP-X-10": ("(exp(i*theta))^n",),
    "VC-OP-X-11": ("1/(1-exp(i*theta))",),
    "VC-OP-X-12": ("abs(1+exp(i*theta))",),
}

# Valor exacto congelado, derivado de la matriz y reproducido por el oráculo.
EXPECTED = {
    "VC-OP-B-01": (3 + 2 * I,),
    "VC-OP-B-02": (1 + 4 * I,),
    "VC-OP-B-03": (5 + I,),
    "VC-OP-B-04": (-1 + 2 * I,),
    "VC-OP-B-05": (sympy.Rational(-7, 25) + 24 * I / 25,),
    "VC-OP-B-06": (-1,),
    "VC-OP-B-07": (32 * I,),
    "VC-OP-B-08": (I,),
    "VC-OP-B-09": (3 + 4 * I, 5),
    "VC-OP-B-10": (sympy.Rational(1, 2), sympy.Rational(-1, 2)),
    "VC-OP-B-11": (sympy.Rational(1, 2) - 3 * I / 2,),
    "VC-OP-P-01": (6 * I,),
    "VC-OP-P-02": (4 * I,),
    "VC-OP-P-03": (8 * I,),
    "VC-OP-P-04": (-4,),
    "VC-OP-P-05": (sympy.Rational(1, 4) - sympy.sqrt(3) * I / 4,),
    "VC-OP-P-06": (
        sympy.Rational(3, 4)
        + 3 * sympy.sqrt(5) / 4
        - 3 * sympy.sqrt(-10 + 2 * sympy.sqrt(5)) / 4,
    ),
    "VC-OP-P-07": (-6 * I,),
    "VC-OP-P-08": (1,),
    "VC-OP-P-09": (256,),
    "VC-OP-T-01": (I,),
    "VC-OP-T-02": (8 + 8 * sympy.sqrt(3) * I,),
    "VC-OP-T-03": (I,),
    "VC-OP-T-05": (sympy.exp(I * (ALPHA + BETA)),),
    "VC-OP-X-01": (I,),
    "VC-OP-X-02": (-I,),
    "VC-OP-X-03": (1,),
    "VC-OP-X-04": (-16 * sympy.sqrt(3) + 16 * I,),
    "VC-OP-X-05": (2 * sympy.cos(THETA),),
    "VC-OP-X-06": (2 * I * sympy.sin(THETA),),
    "VC-OP-X-07": (0,),
    "VC-OP-X-08": (3 * sympy.exp(-I * THETA), REAL_R * sympy.exp(-I * THETA)),
    "VC-OP-X-09": (sympy.exp(REAL_A),),
}

PASS = {
    "VC-OP-B-01",
    "VC-OP-B-02",
    "VC-OP-B-03",
    "VC-OP-B-04",
    "VC-OP-B-05",
    "VC-OP-B-06",
    "VC-OP-B-07",
    "VC-OP-B-08",
    "VC-OP-B-09",
    "VC-OP-B-10",
    "VC-OP-B-11",
    "VC-OP-T-01",
    "VC-OP-T-02",
    "VC-OP-T-03",
    "VC-OP-X-01",
    "VC-OP-X-02",
    "VC-OP-X-03",
    "VC-OP-X-05",
    "VC-OP-X-06",
    "VC-OP-X-07",
}
PASS_SCOPED = {
    "VC-OP-P-01",
    "VC-OP-P-02",
    "VC-OP-P-03",
    "VC-OP-P-04",
    "VC-OP-P-05",
    "VC-OP-P-06",
    "VC-OP-P-07",
    "VC-OP-P-08",
    "VC-OP-P-09",
    "VC-OP-T-05",
    "VC-OP-X-04",
    "VC-OP-X-08",
    "VC-OP-X-09",
}
BLOCKED = {
    "VC-OP-T-04",
    "VC-OP-T-06",
    "VC-OP-T-07",
    "VC-OP-T-08",
    "VC-OP-T-09",
    "VC-OP-X-10",
    "VC-OP-X-11",
    "VC-OP-X-12",
}
TRANSLATED = {row_id for row_id in B2_IDS if row_id.startswith("VC-OP-P-")}

# Notación polar literal de la fuente, rechazada por el canal.
RAW_POLAR = {
    "VC-OP-P-01": ("2_{pi/6}", "3_{pi/3}"),
    "VC-OP-P-02": ("8_{pi}", "2_{pi/2}"),
    "VC-OP-P-03": ("(2_{pi/6})^3",),
    "VC-OP-P-04": ("(sqrt(2)_{pi/4})^4",),
    "VC-OP-P-05": ("1/(2_{pi/3})",),
    "VC-OP-P-06": ("conj(3_{pi/5})",),
    "VC-OP-P-07": ("2_{3*pi/4}", "3_{3*pi/4}"),
    "VC-OP-P-08": ("(1_{pi/3})^6",),
    "VC-OP-P-09": ("(2_{-pi/4})^8",),
}

# Oráculo polar: la aritmética de módulo/argumento de la fuente, calculada por
# sympy sin pasar por el producto.
POLAR_ORACLE = {
    "VC-OP-P-01": 2 * sympy.exp(I * PI / 6) * 3 * sympy.exp(I * PI / 3),
    "VC-OP-P-02": 8 * sympy.exp(I * PI) / (2 * sympy.exp(I * PI / 2)),
    "VC-OP-P-03": (2 * sympy.exp(I * PI / 6)) ** 3,
    "VC-OP-P-04": (sympy.sqrt(2) * sympy.exp(I * PI / 4)) ** 4,
    "VC-OP-P-05": 1 / (2 * sympy.exp(I * PI / 3)),
    "VC-OP-P-06": sympy.conjugate(3 * sympy.exp(I * PI / 5)),
    "VC-OP-P-07": 2 * sympy.exp(I * 3 * PI / 4) * 3 * sympy.exp(I * 3 * PI / 4),
    "VC-OP-P-08": (sympy.exp(I * PI / 3)) ** 6,
    "VC-OP-P-09": (2 * sympy.exp(-I * PI / 4)) ** 8,
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
    """Identidad exacta probando varias normalizaciones simbólicas."""
    normalizations = (
        lambda e: e,
        lambda e: sympy.expand(e, complex=True),
        lambda e: sympy.expand_trig(e),
        lambda e: e.rewrite(sympy.exp),
        lambda e: sympy.trigsimp(e),
        lambda e: sympy.simplify(e.rewrite(sympy.exp)),
    )
    for normalize in normalizations:
        try:
            candidate = normalize(expression)
        except Exception:  # noqa: BLE001 - sympy lanza tipos variados
            continue
        for simplify in (sympy.simplify, sympy.trigsimp):
            try:
                if simplify(candidate) == 0:
                    return True
            except Exception:  # noqa: BLE001 - sympy lanza tipos variados
                continue
    return False


def test_edcx_fixture_b2_matches_the_frozen_source():
    assert len(ROWS) == 638
    assert len(B2) == 41
    assert set(SOURCES) == B2_IDS
    assert set(EXPECTED) == PASS | PASS_SCOPED
    assert PASS | PASS_SCOPED | BLOCKED == B2_IDS
    assert not (PASS & PASS_SCOPED or PASS & BLOCKED or PASS_SCOPED & BLOCKED)
    assert len(PASS) == 20 and len(PASS_SCOPED) == 13 and len(BLOCKED) == 8
    assert set(RAW_POLAR) == TRANSLATED
    assert set(POLAR_ORACLE) == TRANSLATED


@pytest.mark.parametrize("row_id", sorted(PASS))
def test_edcx_b2_exact_rows_return_the_frozen_value(row_id):
    client = TestClient(app)
    sources = SOURCES[row_id]
    expected = EXPECTED[row_id]
    assert len(sources) == len(expected)
    for expression, value in zip(sources, expected, strict=True):
        body = _evaluate(client, expression)
        assert body["success"] is True, (row_id, expression, body)
        assert _same(_parse(body["result_text"]), value), (row_id, body["result_text"])


@pytest.mark.parametrize("row_id", sorted(TRANSLATED))
def test_edcx_b2_p_rows_require_documented_polar_translation(row_id):
    client = TestClient(app)

    for raw in RAW_POLAR[row_id]:
        body = _evaluate(client, raw)
        assert body["success"] is False
        assert body["error_code"] == "PARSE_ERROR"

    # La traducción documentada r_theta -> r*(cos(theta)+i*sin(theta)) sí evalúa.
    body = _evaluate(client, SOURCES[row_id][0])
    assert body["success"] is True
    result = _parse(body["result_text"])
    assert _same(result, EXPECTED[row_id][0])
    assert _same(result, POLAR_ORACLE[row_id])


def test_edcx_b2_euler_product_is_returned_in_exponential_form():
    client = TestClient(app)
    body = _evaluate(client, SOURCES["VC-OP-T-05"][0])
    assert body["success"] is True
    assert body["result_text"] == "exp(I*(alpha + beta))"
    assert _same(_parse(body["result_text"]), EXPECTED["VC-OP-T-05"][0])

    # Oráculo: el producto trigonométrico es exactamente e^{i(alpha+beta)}.
    product = (sympy.cos(ALPHA) + I * sympy.sin(ALPHA)) * (
        sympy.cos(BETA) + I * sympy.sin(BETA)
    )
    assert _is_zero(product - (sympy.cos(ALPHA + BETA) + I * sympy.sin(ALPHA + BETA)))
    assert _is_zero(
        sympy.exp(I * (ALPHA + BETA))
        - (sympy.cos(ALPHA + BETA) + I * sympy.sin(ALPHA + BETA))
    )


def test_edcx_b2_x04_principal_root_equals_the_cartesian_value():
    client = TestClient(app)
    body = _evaluate(client, SOURCES["VC-OP-X-04"][0])
    assert body["success"] is True
    assert body["result_text"] == "32*(-1)**(5/6)"
    assert _same(_parse(body["result_text"]), -16 * sympy.sqrt(3) + 16 * I)
    assert _same((2 * sympy.exp(I * PI / 6)) ** 5, -16 * sympy.sqrt(3) + 16 * I)


def test_edcx_b2_conjugate_rows_keep_the_conjugate_symbol():
    client = TestClient(app)

    body = _evaluate(client, SOURCES["VC-OP-X-08"][0])
    assert body["success"] is True
    assert body["result_text"] == "3*exp(-I*conjugate(theta))"
    assert _same(_parse(body["result_text"]), 3 * sympy.exp(-I * THETA))
    assert _is_zero(sympy.conjugate(3 * sympy.exp(I * THETA)) - 3 * sympy.exp(-I * THETA))

    body = _evaluate(client, SOURCES["VC-OP-X-08"][1])
    assert body["success"] is True
    assert body["result_text"] == "exp(-I*conjugate(theta))*conjugate(r)"
    assert _same(_parse(body["result_text"]), REAL_R * sympy.exp(-I * THETA))
    assert _is_zero(sympy.conjugate(REAL_R * sympy.exp(I * THETA)) - REAL_R * sympy.exp(-I * THETA))


def test_edcx_b2_absolute_value_applies_real_part_and_imaginary_part():
    client = TestClient(app)
    body = _evaluate(client, SOURCES["VC-OP-X-09"][0])
    assert body["success"] is True
    assert body["result_text"] == "exp(re(a) - im(b))"
    assert _same(_parse(body["result_text"]), sympy.exp(REAL_A))
    # Oráculo: con a y b reales, |e^{a+bi}| = e^{a}.
    assert _is_zero(sympy.Abs(sympy.exp(REAL_A + I * REAL_B)) - sympy.exp(REAL_A))


def test_edcx_b2_blocked_multiple_angle_expansions_are_not_produced():
    client = TestClient(app)

    # T-04: la potencia no se combina; se devuelve la base exponencial.
    body = _evaluate(client, SOURCES["VC-OP-T-04"][0])
    assert body["success"] is True
    assert body["result_text"] == "exp(I*theta)**n"
    for n in (2, 3, 4, 5, 7):
        assert _is_zero(
            (sympy.cos(THETA) + I * sympy.sin(THETA)) ** n
            - (sympy.cos(n * THETA) + I * sympy.sin(n * THETA))
        )

    # T-06/T-07/T-08: la entrada se devuelve sin expandir ni linealizar.
    body = _evaluate(client, SOURCES["VC-OP-T-06"][0])
    assert body["result_text"] == "cos(3*theta)"
    assert _is_zero(sympy.cos(3 * THETA) - (4 * sympy.cos(THETA) ** 3 - 3 * sympy.cos(THETA)))

    body = _evaluate(client, SOURCES["VC-OP-T-07"][0])
    assert body["result_text"] == "sin(3*theta)"
    assert _is_zero(sympy.sin(3 * THETA) - (3 * sympy.sin(THETA) - 4 * sympy.sin(THETA) ** 3))

    body = _evaluate(client, SOURCES["VC-OP-T-08"][0])
    assert body["result_text"] == "cos(theta)**4"
    assert _is_zero(
        sympy.cos(THETA) ** 4 - (3 + 4 * sympy.cos(2 * THETA) + sympy.cos(4 * THETA)) / 8
    )

    # Hallazgo de notación: `cos3theta` se lee como un símbolo libre.
    body = _evaluate(client, "cos3theta")
    assert body["success"] is True
    assert body["result_text"] == "cos3theta"


def test_edcx_b2_blocked_summation_has_no_parser():
    client = TestClient(app)
    for raw in SOURCES["VC-OP-T-09"]:
        body = _evaluate(client, raw)
        assert body["success"] is False
        assert body["error_code"] == "PARSE_ERROR"

    # Oráculo: la forma cerrada de la matriz es correcta para n = 0..6.
    for n in range(7):
        lhs = sympy.summation(sympy.cos(K * THETA), (K, 0, n))
        rhs = sympy.sin((n + 1) * THETA / 2) * sympy.cos(n * THETA / 2) / sympy.sin(THETA / 2)
        assert _is_zero(lhs - rhs), n


def test_edcx_b2_blocked_exponential_rows_are_echoed_unreduced():
    client = TestClient(app)

    # X-10: (e^{i theta})^n no se combina en e^{i n theta}.
    body = _evaluate(client, SOURCES["VC-OP-X-10"][0])
    assert body["success"] is True
    assert body["result_text"] == "exp(I*theta)**n"
    for n in (2, 3, 4, 5, 7):
        assert _is_zero((sympy.exp(I * THETA)) ** n - sympy.exp(I * n * THETA))

    # X-11: no hay reescritura de serie geométrica.
    body = _evaluate(client, SOURCES["VC-OP-X-11"][0])
    assert body["success"] is True
    assert body["result_text"] == "1/(1 - exp(I*theta))"
    assert _is_zero(
        1 / (1 - sympy.exp(I * THETA))
        - (sympy.Rational(1, 2) + I * sympy.cot(THETA / 2) / 2)
    )

    # X-12: |1+e^{i theta}| no se reduce a 2|cos(theta/2)|.
    body = _evaluate(client, SOURCES["VC-OP-X-12"][0])
    assert body["success"] is True
    assert body["result_text"] == "Abs(exp(I*theta) + 1)"
    # Ambos miembros son no negativos, así que la igualdad de cuadrados basta.
    assert _is_zero(
        sympy.Abs(1 + sympy.exp(I * THETA)) ** 2 - 4 * sympy.cos(THETA / 2) ** 2
    )


def test_edcx_b2_classification_counts_are_explicit():
    assert len(B2) == 41
    assert PASS | PASS_SCOPED | BLOCKED == B2_IDS
    assert len(PASS) == 20
    assert len(PASS_SCOPED) == 13
    assert len(BLOCKED) == 8
    assert PASS == {
        "VC-OP-B-01",
        "VC-OP-B-02",
        "VC-OP-B-03",
        "VC-OP-B-04",
        "VC-OP-B-05",
        "VC-OP-B-06",
        "VC-OP-B-07",
        "VC-OP-B-08",
        "VC-OP-B-09",
        "VC-OP-B-10",
        "VC-OP-B-11",
        "VC-OP-T-01",
        "VC-OP-T-02",
        "VC-OP-T-03",
        "VC-OP-X-01",
        "VC-OP-X-02",
        "VC-OP-X-03",
        "VC-OP-X-05",
        "VC-OP-X-06",
        "VC-OP-X-07",
    }
    assert BLOCKED == {
        "VC-OP-T-04",
        "VC-OP-T-06",
        "VC-OP-T-07",
        "VC-OP-T-08",
        "VC-OP-T-09",
        "VC-OP-X-10",
        "VC-OP-X-11",
        "VC-OP-X-12",
    }
