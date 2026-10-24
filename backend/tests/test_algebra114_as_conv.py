"""Algebra114 AS-CONV-01..08 (sección L): convenciones matemáticas.

Contrato (qa/certification/algebra114_source.md, sección L): el motor debe
DECLARAR la convención cuando una expresión es ambigua entre ℝ y ℂ, y debe
devolver el VALOR que el contrato fija (|x|, no x; |x-1|; |x-3|+|x+3|).
La declaración viaja en `warnings` de `MathResponse`.

Reglas de honestidad de este archivo (CURRENT_STATE 2026-10-20):

* El oráculo de cada caso es el resultado que exige el contrato; no existen
  ramas «o declarada» que aprueben un valor incorrecto con una nota.
* Alcance verificado: `POST /api/v1/simplify`. El endpoint `/api/v1/evaluate`
  resuelve estas convenciones en silencio y está registrado abajo como
  `xfail(strict)` (capability gap acotado), no como PASS.
* Una declaración solo cuenta si describe un cálculo que el motor hizo.
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


def _post(endpoint: str, expression: str) -> dict:
    response = client.post(f"/api/v1/{endpoint}", json={"expression": expression})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True, body
    return body


def _simplify(expression: str) -> dict:
    return _post("simplify", expression)


def _declares(body: dict, tag: str) -> bool:
    """True si alguna advertencia lleva la etiqueta de convención pedida."""
    return any(tag in w for w in body.get("warnings", []))


def _value(body: dict) -> sp.Expr:
    return sp.sympify(body["result_text"])


def test_as_conv_fixture_rows_present():
    for case in range(1, 9):
        assert f"| AS-CONV-0{case} |" in SOURCE


# --- AS-CONV-01: ∛(-8) = -2 en ℝ (o 1+i√3 en la rama principal de ℂ), declarada ---


def test_as_conv_01_real_cube_root_of_negative_declared():
    body = _simplify("root(-8,3)")
    assert _value(body) == -2
    assert _declares(body, "AS-CONV-01")


# --- AS-CONV-02: (-8)^(2/3): 4 (real) o -2+2i√3 (principal ℂ), convención declarada ---


def test_as_conv_02_rational_power_of_negative_declares_principal_branch():
    body = _simplify("(-8)**(2/3)")
    principal = -2 + 2 * sp.sqrt(3) * sp.I
    assert sp.simplify(sp.expand_complex(_value(body)) - principal) == 0
    assert _declares(body, "AS-CONV-02")


# --- AS-CONV-03: x^0 = 1; 0^0 declarado, nunca en silencio, sea cual sea su forma ---


def test_as_conv_03_x0_is_one_and_makes_no_zero_zero_claim():
    for expression in ("x**0", "2**0", "0**2"):
        body = _simplify(expression)
        assert not _declares(body, "AS-CONV-03"), (expression, body["warnings"])
    assert _value(_simplify("x**0")) == 1


def test_as_conv_03_zero_to_zero_literal_declared():
    body = _simplify("0**0")
    assert _value(body) == 1
    assert _declares(body, "AS-CONV-03")


@pytest.mark.xfail(
    strict=True,
    reason="AS-CONV-03: 0^0 solo se declara para el texto literal; (1-1)**(1-1), 0**(2-2), "
    "0**0+1 y 2**0+0**0 devuelven 1 en silencio",
)
def test_as_conv_03_every_form_that_is_zero_to_zero_is_declared():
    for expression in ("(1-1)**(1-1)", "0**(2-2)", "0**0+1", "2**0+0**0"):
        body = _simplify(expression)
        assert _declares(body, "AS-CONV-03"), (expression, body["warnings"])


# --- AS-CONV-04: sqrt(-4): 2i en ℂ con el dominio complejo declarado ---


def test_as_conv_04_sqrt_negative_declares_complex_domain():
    body = _simplify("sqrt(-4)")
    assert _value(body) == 2 * sp.I
    assert _declares(body, "AS-CONV-04")


# --- AS-CONV-05..08: el contrato fija el VALOR |u| (no u) ---


def test_as_conv_05_fourth_root_x4_is_abs_x():
    assert _value(_simplify("root(x**4,4)")) == sp.Abs(x)


def test_as_conv_06_cbrt_x3_is_x_without_convention_noise():
    body = _simplify("root(x**3,3)")
    assert _value(body) == x
    assert not _declares(body, "AS-CONV"), body["warnings"]


def test_as_conv_07_sqrt_perfect_square_is_abs():
    assert _value(_simplify("sqrt(x**2-2*x+1)")) == sp.Abs(x - 1)


def test_as_conv_08_sum_of_roots_is_abs_sum():
    value = _value(_simplify("sqrt(x**2-6*x+9)+sqrt(x**2+6*x+9)"))
    assert sp.simplify(value - (sp.Abs(x - 3) + sp.Abs(x + 3))) == 0
    assert value.has(sp.Abs)
    assert not value.has(sp.sqrt)


def test_as_conv_controls_non_perfect_powers_are_not_rewritten_to_abs():
    for expression in ("sqrt(x**2+1)", "sqrt(x**2-2*x+2)", "sqrt(x**3)"):
        assert not _value(_simplify(expression)).has(sp.Abs), expression


# --- Alcance: /evaluate resuelve las convenciones en silencio (capability gap acotado) ---


@pytest.mark.xfail(
    strict=True,
    reason="AS-CONV: POST /api/v1/evaluate no emite advertencias de convención "
    "(0**0, root(-8,3), sqrt(-4), (-8)**(2/3)); solo /simplify las declara",
)
def test_as_conv_evaluate_endpoint_declares_conventions():
    for expression in ("0**0", "root(-8,3)", "sqrt(-4)", "(-8)**(2/3)"):
        body = _post("evaluate", expression)
        assert any("AS-CONV" in w for w in body.get("warnings", [])), (expression, body["warnings"])
