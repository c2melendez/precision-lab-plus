"""Log/Exp matrix EV-T-01..12: trigonometric, hyperbolic and inverse rows.

Bilateral coverage for the EV-T rows of matriz_log_exp_radicales. The frozen
matrix is LaTeX; this API evaluates the documented plain translation of each
row (same convention as EV-E, EV-M and EV-R). The ``operatorname{arsinh}`` and
``operatorname{artanh}`` spellings are translated to their flat forms
(``asinh``/``atanh``): the frontend alias table maps ``arsinh -> operatorname{asinh}``
and ``artanh -> operatorname{atanh}`` (NaturalMathField.tsx), and the backend
recognises the flat spellings. Each test asserts that the row exists in the
frozen source and compares the engine output against the exact value or the
nine-decimal reference printed in that row.
"""
from pathlib import Path
import gzip
import re

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app

SOURCE_GZ = (
    Path(__file__).resolve().parents[2]
    / "qa/certification/legacy_sources/matriz_log_exp_radicales.md.gz"
)

# Plain translations of the frozen LaTeX rows. Literal row text is asserted
# separately in test_ev_t_source_rows_present.
EXPRESSIONS = {
    "EV-T-01": "ln(sin(pi/2))",
    "EV-T-02": "e^(sin(pi/6))",
    "EV-T-03": "sqrt(1+tan(pi/3)^2)",
    "EV-T-04": "ln(tan(pi/4))",
    "EV-T-05": "ln(cosh(1))",
    "EV-T-06": "arctan(e^0)",
    "EV-T-07": "sin(10^22)",
    "EV-T-08": "e^(i*pi/2)",
    "EV-T-09": "asinh((e-e^(-1))/2)",
    "EV-T-10": "exp(atanh(1/2))",
    "EV-T-11": "ln(cos(pi/2))",
    "EV-T-12": "sqrt(cos(pi))",
}

_I_LOCALS = {"i": sp.I, "I": sp.I}


def _row(case_id: str) -> str:
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    return next((line for line in text.splitlines() if f"| {case_id} |" in line), "")


def _evaluate(client: TestClient, expression: str) -> dict:
    response = client.post("/api/v1/evaluate", json={"expression": expression})
    assert response.status_code == 200, response.text
    return response.json()


def _value(payload: dict):
    assert payload["success"] is True, payload
    return sp.sympify(payload["result_text"].replace("^", "**"), locals=_I_LOCALS)


def test_ev_t_source_rows_present():
    for index in range(1, 13):
        case_id = f"EV-T-{index:02d}"
        assert _row(case_id), f"{case_id} row missing"


def test_ev_t_frozen_oracles_anchored():
    assert "\\ln\\left(\\sin\\frac{\\pi}{2}\\right)" in _row("EV-T-01")
    assert "e^{\\sin(\\pi/6)}" in _row("EV-T-02")
    assert "\\sqrt{1+\\tan^{2}\\frac{\\pi}{3}}" in _row("EV-T-03")
    assert "\\ln\\left(\\tan\\frac{\\pi}{4}\\right)" in _row("EV-T-04")
    assert "\\ln(\\cosh 1)" in _row("EV-T-05")
    assert "0.433780830" in _row("EV-T-05")
    assert "\\arctan\\left(e^{0}\\right)" in _row("EV-T-06")
    assert "\\sin\\left(10^{22}\\right)" in _row("EV-T-07")
    assert "-0.852200850" in _row("EV-T-07")
    assert "e^{i\\pi/2}" in _row("EV-T-08")
    assert "\\operatorname{arsinh}" in _row("EV-T-09")
    assert "\\operatorname{artanh}" in _row("EV-T-10")
    assert "\\ln\\left(\\cos\\frac{\\pi}{2}\\right)" in _row("EV-T-11")
    assert "\\sqrt{\\cos\\pi}" in _row("EV-T-12")


def test_ev_t_exact_values():
    exact = [
        ("EV-T-01", sp.Integer(0)),
        ("EV-T-02", sp.sqrt(sp.E)),
        ("EV-T-03", sp.Integer(2)),
        ("EV-T-04", sp.Integer(0)),
        ("EV-T-06", sp.pi / 4),
        ("EV-T-09", sp.Integer(1)),
        ("EV-T-10", sp.sqrt(3)),
    ]
    with TestClient(app) as client:
        for case_id, expected in exact:
            payload = _evaluate(client, EXPRESSIONS[case_id])
            assert sp.simplify(_value(payload) - expected) == 0, (case_id, payload)


def test_ev_t_exact_rows_keep_a_symbolic_form():
    # Protocolo, regla 2: una salida que solo imprima el decimal no certifica.
    # Un entero exacto (EV-T-09 -> 1) no es una aproximacion decimal: la
    # prohibicion aplica a valores con punto decimal, no a enteros.
    plain_decimal = re.compile(r"-?\d+\.\d+([eE][+-]?\d+)?")
    with TestClient(app) as client:
        for case_id in ("EV-T-02", "EV-T-05", "EV-T-07", "EV-T-09", "EV-T-10"):
            payload = _evaluate(client, EXPRESSIONS[case_id])
            assert not plain_decimal.fullmatch(payload["result_text"].strip()), (
                case_id,
                payload,
            )


def test_ev_t08_and_t12_use_the_documented_complex_branch():
    with TestClient(app) as client:
        # La fila documenta i en C; Plus imprime la unidad imaginaria de SymPy.
        assert _value(_evaluate(client, "e^(i*pi/2)")) == sp.I
        assert _value(_evaluate(client, "sqrt(cos(pi))")) == sp.I
        # Control del canal complejo.
        assert sp.simplify(_value(_evaluate(client, "ln(-1)")) - sp.I * sp.pi) == 0


def test_ev_t11_requires_domain_error_and_closes_the_log_leak():
    with TestClient(app) as client:
        for expression in ("ln(cos(pi/2))", "ln(1-1)", "ln(0)", "ln(0+0)", "log(0,10)"):
            payload = _evaluate(client, expression)
            assert payload["success"] is False, (expression, payload)
            assert payload["error_code"] == "DOMAIN_ERROR", (expression, payload)
            assert payload.get("result_text") in (None, ""), (expression, payload)
        # Los logaritmos válidos del mismo canal siguen intactos.
        assert _value(_evaluate(client, "ln(e)")) == 1
        assert _value(_evaluate(client, "log(100)")) == 2
        assert _value(_evaluate(client, "ln(sin(pi/2))")) == 0


def test_ev_t_approximation_rows_match_the_frozen_reference():
    # (id, referencia congelada, valor): el oraculo del test debe aparecer
    # literalmente en la fila congelada de la matriz.
    references = [
        ("EV-T-05", "0.433780830", 0.433780830),
        ("EV-T-07", "-0.852200850", -0.852200850),
    ]
    with TestClient(app) as client:
        for case_id, frozen, reference in references:
            assert frozen in _row(case_id), case_id
            payload = _evaluate(client, EXPRESSIONS[case_id])
            assert abs(payload["result_approx"] - reference) <= 5e-10, (
                case_id,
                payload,
            )
