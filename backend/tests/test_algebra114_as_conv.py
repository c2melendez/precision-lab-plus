"""Algebra114 AS-CONV-01..08 (sección L): convenciones matemáticas.

El contrato exige que el motor DECLARE la convención usada cuando una
expresión es ambigua entre ℝ y ℂ, o cuando una identidad depende de
supuestos sobre las variables. La declaración viaja en `warnings` del
contrato `MathResponse` (canal contractual vigente; ver CURRENT_STATE.md
2026-10-20). Los valores numéricos por sí solos no prueban conformidad:
`(-8)**(2/3) = 4` (convención real) y `-2+2i√3` (rama principal ℂ) son
ambos "correctos" bajo su convención — lo que el contrato prohíbe es
resolver en silencio.

Test-first: los casos con GAP conocidos se marcan con `xfail(strict)` y
enlazan a MANUAL_CAPABILITY_GAPS.md; un PASS espurio no puede borrarlos.
"""

from pathlib import Path

import pytest
import sympy as sp
from fastapi.testclient import TestClient

from app.main import app

x = sp.Symbol("x")
client = TestClient(app)
SOURCE = (Path(__file__).resolve().parents[2] / "qa/certification/algebra114_source.md").read_text(
    encoding="utf-8"
)


def _simplify(expression: str) -> dict:
    response = client.post("/api/v1/simplify", json={"expression": expression})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    return body


def _has_convention(body: dict, needle: str) -> bool:
    """True si alguna advertencia declara la convención pedida."""
    return any(needle.lower() in w.lower() for w in body.get("warnings", []))


# --- Casos sin ambigüedad: comportamiento correcto SIN ruido ---


def test_as_conv_06_cbrt_x3_is_x_without_warning():
    # AS-CONV-06: ∛(x^3) = x (impar ⇒ válida en ℝ sin supuestos).
    assert "| AS-CONV-06 |" in SOURCE
    body = _simplify("root(x**3,3)")
    actual = sp.sympify(body["result_text"])
    assert sp.simplify(actual - x) == 0, actual
    assert not _has_convention(body, "raíz"), body["warnings"]


def test_as_conv_03_x0_is_one_for_nonzero_base():
    # AS-CONV-03: x^0 = 1 para x ≠ 0 (variable ⇒ x≠0 es supuesto estándar
    # del álgebra simbólica; no requiere declaración).
    assert "| AS-CONV-03 |" in SOURCE
    body = _simplify("x**0")
    assert sp.sympify(body["result_text"]) == 1


# --- Casos que exigen DECLARACIÓN explícita de convención ---


@pytest.mark.xfail(
    strict=True,
    reason="GAP AS-CONV-01: root(-8,3) devuelve 2*(-1)**(1/3) (rama principal ℂ) "
    "sin declarar convención; debe devolver -2 (raíz real) o declarar ℂ. "
    "Ver MANUAL_CAPABILITY_GAPS.md (AS-CONV).",
)
def test_as_conv_01_real_cube_root_of_negative_declared():
    assert "| AS-CONV-01 |" in SOURCE
    body = _simplify("root(-8,3)")
    value = sp.sympify(body["result_text"])
    if value == -2:
        # Aceptable solo si además declara que eligió la rama real.
        assert _has_convention(body, "raíz real") or _has_convention(body, "real")
    else:
        # Rama principal compleja: debe declararse explícitamente.
        assert _has_convention(body, "compleja") or _has_convention(body, "principal")


@pytest.mark.xfail(
    strict=True,
    reason="GAP AS-CONV-02: (-8)**(2/3) resuelto en silencio; el contrato exige "
    "declarar convención real (4) o rama principal ℂ (-2+2i√3). "
    "Ver MANUAL_CAPABILITY_GAPS.md (AS-CONV).",
)
def test_as_conv_02_rational_power_of_negative_declares_convention():
    assert "| AS-CONV-02 |" in SOURCE
    body = _simplify("(-8)**(2/3)")
    assert _has_convention(body, "convención") or _has_convention(body, "rama principal")


@pytest.mark.xfail(
    strict=True,
    reason="GAP AS-CONV-03: 0**0 = 1 resuelto en silencio; el contrato exige "
    "declarar la convención (límite combinatorio) o señalar indeterminación. "
    "Ver MANUAL_CAPABILITY_GAPS.md (AS-CONV).",
)
def test_as_conv_03_zero_to_zero_declared_not_silent():
    assert "| AS-CONV-03 |" in SOURCE
    body = _simplify("0**0")
    assert _has_convention(body, "0^0") or _has_convention(body, "indeterminad")


@pytest.mark.xfail(
    strict=True,
    reason="GAP AS-CONV-04: sqrt(-4)=2*I sin declarar que opera en ℂ; en ℝ sería "
    "error claro. Ver MANUAL_CAPABILITY_GAPS.md (AS-CONV).",
)
def test_as_conv_04_sqrt_negative_declares_complex_domain():
    assert "| AS-CONV-04 |" in SOURCE
    body = _simplify("sqrt(-4)")
    value = sp.sympify(body["result_text"])
    if value == 2 * sp.I:
        assert _has_convention(body, "compleja") or _has_convention(body, "ℂ")
    else:
        pytest.fail("sqrt(-4) debe devolver 2i (con declaración ℂ) o DOMAIN_ERROR")


@pytest.mark.xfail(
    strict=True,
    reason="GAP AS-CONV-05: root(x**4,4) no se simplifica a Abs(x) ni declara el "
    "supuesto x≥0. Ver MANUAL_CAPABILITY_GAPS.md (AS-CONV).",
)
def test_as_conv_05_fourth_root_x4_is_abs_x_or_declared():
    assert "| AS-CONV-05 |" in SOURCE
    body = _simplify("root(x**4,4)")
    value = sp.sympify(body["result_text"])
    if value == sp.Abs(x):
        return
    assert _has_convention(body, "x ≥ 0") or _has_convention(body, "supuesto")


@pytest.mark.xfail(
    strict=True,
    reason="GAP AS-CONV-07: sqrt(x^2-2x+1) no se simplifica a Abs(x-1) ni declara "
    "supuesto. Ver MANUAL_CAPABILITY_GAPS.md (AS-CONV).",
)
def test_as_conv_07_sqrt_perfect_square_is_abs_or_declared():
    assert "| AS-CONV-07 |" in SOURCE
    body = _simplify("sqrt(x**2-2*x+1)")
    value = sp.sympify(body["result_text"])
    if value == sp.Abs(x - 1):
        return
    assert _has_convention(body, "supuesto") or _has_convention(body, "x ≥ 1")


@pytest.mark.xfail(
    strict=True,
    reason="GAP AS-CONV-08: suma de raíces de trinomios cuadrados perfectos no "
    "produce |x-3|+|x+3| ni declara convención. Ver MANUAL_CAPABILITY_GAPS.md (AS-CONV).",
)
def test_as_conv_08_sum_of_roots_is_abs_sum_or_declared():
    assert "| AS-CONV-08 |" in SOURCE
    body = _simplify("sqrt(x**2-6*x+9)+sqrt(x**2+6*x+9)")
    value = sp.sympify(body["result_text"])
    expected = sp.Abs(x - 3) + sp.Abs(x + 3)
    if sp.simplify(value - expected) == 0:
        return
    assert _has_convention(body, "supuesto") or _has_convention(body, "valor absoluto")
