"""EDCX Parte B — B3 "Potencias y raíces" (19 filas, VC-PR-01..19).

Canal
-----
`/api/v1/evaluate` resuelve potencias enteras y negativas de forma exacta
(`(1+i*sqrt(3))^9 = -512`) y devuelve la raíz principal de `sqrt(z)` y de
`root(z, n)`. No existe un endpoint de raíces n-ésimas ni un operador que
enumere todas las raíces: `8^(1/3)` devuelve solo `2` y `1^(1/4)` devuelve
solo `1`.

La enumeración completa se certifica con `/api/v1/solve` sobre la ecuación
`z^n = w`, que devuelve todas las soluciones en `result_data`. Es una ruta
alternativa documentada, no una operación de raíz n-ésima del producto; por
eso las filas que piden «todas las raíces» se clasifican PASS_SCOPED.

Clasificación
-------------
- PASS (7): PR-01..PR-06 y PR-19. Una sola evaluación devuelve exactamente el
  valor congelado. PR-19 certifica el valor `cos(2*pi/5) = (sqrt(5)-1)/4`; la
  derivación pedagógica desde `z^5=1` no se ejecuta.
- PASS_SCOPED (10): PR-07..PR-16. El conjunto de raíces es exacto, pero se
  obtiene resolviendo `z^n=w` (no hay operación de raíz n-ésima) y/o se emite
  en forma cartesiana de radicales en lugar de la forma polar/exponencial
  pedida. PR-07 devuelve `±sqrt(I)`, equivalente exacto de `±(1+i)/sqrt(2)`.
- BLOCKED (2):
  * PR-17: no existe nodo de sumatoria; `sum(...)` y `Sum(...)` devuelven
    `PARSE_ERROR`, aunque la suma geométrica vale 0 para `n >= 2`.
  * PR-18: no existe operación de producto de raíces; `/solve` enumera las
    raíces cuartas de la unidad, pero el producto `(-1)^(n+1)` no se produce.

Los conjuntos de raíces y las identidades se comprueban con oráculos sympy
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
B3 = [row for row in ROWS if row["bloque"] == "B3"]
B3_IDS = {row["id"] for row in B3}

I = sympy.I  # noqa: E741 - unidad imaginaria, notación matemática estándar
PI = sympy.pi

LOCALS = {
    "I": I,
    "pi": PI,
    "exp": sympy.exp,
    "sqrt": sympy.sqrt,
    "cos": sympy.cos,
    "sin": sympy.sin,
}

# Evaluación directa: potencias y valor trigonométrico exacto.
SOURCES = {
    "VC-PR-01": "(1+i*sqrt(3))^9",
    "VC-PR-02": "(sqrt(3)-i)^6",
    "VC-PR-03": "((-1+i*sqrt(3))/2)^3",
    "VC-PR-04": "(1+i)^20",
    "VC-PR-05": "(1+i)^(-4)",
    "VC-PR-06": "((1+i)/sqrt(2))^8",
    "VC-PR-19": "cos(2*pi/5)",
}

EXPECTED = {
    "VC-PR-01": -512,
    "VC-PR-02": -64,
    "VC-PR-03": 1,
    "VC-PR-04": -1024,
    "VC-PR-05": sympy.Rational(-1, 4),
    "VC-PR-06": 1,
    "VC-PR-19": (sympy.sqrt(5) - 1) / 4,
}

# Conjunto completo de raíces: ecuación equivalente y valor esperado.
ROOT_SETS = {
    "VC-PR-07": ("z^2=i", ((1 + I) / sympy.sqrt(2), -(1 + I) / sympy.sqrt(2))),
    "VC-PR-08": ("z^2=-3+4*i", (1 + 2 * I, -1 - 2 * I)),
    "VC-PR-09": ("z^2=5-12*i", (3 - 2 * I, -3 + 2 * I)),
    "VC-PR-10": ("z^3=8", (2, -1 + I * sympy.sqrt(3), -1 - I * sympy.sqrt(3))),
    "VC-PR-11": ("z^3=-8", (-2, 1 + I * sympy.sqrt(3), 1 - I * sympy.sqrt(3))),
    "VC-PR-12": (
        "z^3=i",
        (sympy.sqrt(3) / 2 + I / 2, -sympy.sqrt(3) / 2 + I / 2, -I),
    ),
    "VC-PR-13": ("z^4=-4", (1 + I, 1 - I, -1 + I, -1 - I)),
    "VC-PR-14": ("z^4=1", (1, I, -1, -I)),
    "VC-PR-15": (
        "z^6=1",
        tuple(sympy.exp(I * PI * k / 3) for k in range(6)),
    ),
}

PASS = set(SOURCES)
PASS_SCOPED = {
    "VC-PR-07",
    "VC-PR-08",
    "VC-PR-09",
    "VC-PR-10",
    "VC-PR-11",
    "VC-PR-12",
    "VC-PR-13",
    "VC-PR-14",
    "VC-PR-15",
    "VC-PR-16",
}
BLOCKED = {"VC-PR-17", "VC-PR-18"}

PRINCIPAL = 2 ** sympy.Rational(1, 6) * sympy.exp(I * PI / 12)


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


def _solutions(client: TestClient, equation: str) -> list[sympy.Expr]:
    body = _post(client, "/api/v1/solve", {"equation": equation, "variable": "z"})
    assert body["success"] is True, body
    return [sympy.sympify(item["text"], locals=LOCALS) for item in body["result_data"]]


def _same(left, right) -> bool:
    """Igualdad exacta, o a 60 dígitos cuando la forma no se reduce."""
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


def test_edcx_fixture_b3_matches_the_frozen_source():
    assert len(ROWS) == 638
    assert len(B3) == 19
    assert set(SOURCES) | set(ROOT_SETS) | {"VC-PR-16"} | BLOCKED == B3_IDS
    assert PASS | PASS_SCOPED | BLOCKED == B3_IDS
    assert not (PASS & PASS_SCOPED or PASS & BLOCKED or PASS_SCOPED & BLOCKED)
    assert len(PASS) == 7 and len(PASS_SCOPED) == 10 and len(BLOCKED) == 2


@pytest.mark.parametrize("row_id", sorted(PASS))
def test_edcx_b3_direct_rows_return_the_frozen_value(row_id):
    client = TestClient(app)
    body = _evaluate(client, SOURCES[row_id])
    assert body["success"] is True, (row_id, body)
    assert _same(sympy.sympify(body["result_text"], locals=LOCALS), EXPECTED[row_id])


@pytest.mark.parametrize("row_id", sorted(ROOT_SETS))
def test_edcx_b3_root_sets_are_exact_via_solve(row_id):
    client = TestClient(app)
    equation, expected = ROOT_SETS[row_id]
    roots = _solutions(client, equation)
    assert len(roots) == len(expected)
    assert _same_set(roots, expected), (row_id, roots)


def test_edcx_b3_sqrt_channel_only_returns_the_principal_root():
    client = TestClient(app)

    # PR-07: sqrt(i) devuelve la raíz principal sin simplificar; solve da ambas.
    principal = _result(client, "sqrt(i)")
    assert principal == "sqrt(I)"
    assert _same(sympy.sympify(principal, locals=LOCALS), (1 + I) / sympy.sqrt(2))
    assert _same_set(_solutions(client, "z^2=i"), ROOT_SETS["VC-PR-07"][1])

    # PR-08/PR-09: sqrt devuelve solo la raíz principal.
    for row_id, expression, expected_principal in (
        ("VC-PR-08", "sqrt(-3+4*i)", 1 + 2 * I),
        ("VC-PR-09", "sqrt(5-12*i)", 3 - 2 * I),
    ):
        body = _evaluate(client, expression)
        assert body["success"] is True
        assert _same(sympy.sympify(body["result_text"], locals=LOCALS), expected_principal)
        assert _same_set(_solutions(client, ROOT_SETS[row_id][0]), ROOT_SETS[row_id][1])


def test_edcx_b3_principal_cube_root_is_identified_by_argument():
    client = TestClient(app)
    roots = _solutions(client, "z^3=1+i")
    assert len(roots) == 3

    principal = [
        root
        for root in roots
        if complex(sympy.N(root, 30)).real > 0 and complex(sympy.N(root, 30)).imag > 0
    ]
    assert len(principal) == 1
    assert _same(principal[0], PRINCIPAL)
    assert abs(complex(sympy.N(principal[0], 30)) - complex(1.0842150814, 0.2905145555)) < 1e-6


def test_edcx_b3_blocked_summation_has_no_parser():
    client = TestClient(app)
    for raw in ("sum(exp(2*pi*i*k/n), k, 0, n-1)", "Sum(exp(2*pi*i*k/n), (k, 0, n-1))"):
        body = _evaluate(client, raw)
        assert body["success"] is False
        assert body["error_code"] == "PARSE_ERROR"

    # Oráculo: la suma de las n raíces n-ésimas de la unidad es 0 para n >= 2.
    for n in range(2, 9):
        terms = [sympy.exp(2 * PI * I * k / n) for k in range(n)]
        assert _same(sympy.Add(*terms), 0), n


def test_edcx_b3_blocked_root_product_has_no_operation():
    client = TestClient(app)

    # No existe `product`: el identificador se rechaza.
    body = _evaluate(client, "product(1, i, -1, -i)")
    assert body["success"] is False
    assert body["error_code"] == "PARSE_ERROR"

    # El canal sí enumera las raíces cuartas, pero no las multiplica.
    assert len(_solutions(client, "z^4=1")) == 4

    # Oráculo: el producto de las n raíces n-ésimas de la unidad es (-1)^(n+1).
    for n in range(2, 7):
        product = sympy.prod(sympy.exp(2 * PI * I * k / n) for k in range(n))
        assert _same(product, (-1) ** (n + 1)), n


def test_edcx_b3_classification_counts_are_explicit():
    assert len(B3) == 19
    assert PASS | PASS_SCOPED | BLOCKED == B3_IDS
    assert len(PASS) == 7
    assert len(PASS_SCOPED) == 10
    assert len(BLOCKED) == 2
    assert PASS == {
        "VC-PR-01",
        "VC-PR-02",
        "VC-PR-03",
        "VC-PR-04",
        "VC-PR-05",
        "VC-PR-06",
        "VC-PR-19",
    }
    assert BLOCKED == {"VC-PR-17", "VC-PR-18"}
