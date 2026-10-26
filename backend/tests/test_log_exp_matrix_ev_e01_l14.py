"""Log/Exp matrix EV-E-01..14: exponentials.

Bilateral coverage for the exponential rows of matriz_log_exp_radicales.
The frozen matrix mixes exact values, nine-decimal references and one
complex result, so each row is asserted against its documented oracle:
exact rows by symbolic equality, approximation rows by result_approx.
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


def _row(case_id: str) -> str:
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    return next((line for line in text.splitlines() if f"| {case_id} |" in line), "")


def _evaluate(client: TestClient, expression: str) -> dict:
    response = client.post("/api/v1/evaluate", json={"expression": expression})
    assert response.status_code == 200, response.text
    return response.json()


def _value(payload: dict):
    assert payload["success"] is True, payload
    return sp.sympify(payload["result_text"].replace("^", "**"))


def test_ev_e_source_rows_present():
    for index in range(1, 15):
        case_id = f"EV-E-{index:02d}"
        assert _row(case_id), f"{case_id} row missing"


def test_ev_e_exact_values():
    exact = [
        ("e^0", 1),
        ("2^10", 1024),
        ("2^(-3)", sp.Rational(1, 8)),
        ("8^(2/3)", 4),
        ("27^(-1/3)", sp.Rational(1, 3)),
        ("e^(ln(2)+ln(3))", 6),
        ("e^(I*pi)", -1),
    ]
    with TestClient(app) as client:
        for expression, expected in exact:
            payload = _evaluate(client, expression)
            assert sp.simplify(_value(payload) - expected) == 0, (expression, payload)


def test_ev_e_approximations():
    # (id, expresion, referencia congelada, valor): el oraculo del test debe
    # aparecer literalmente en la fila congelada de la matriz.
    references = [
        ("EV-E-02", "e^(-1)", "0.367879441", 0.367879441),
        ("EV-E-07", "2^(sqrt(2))", "2.665144143", 2.665144143),
        ("EV-E-08", "pi^E", "22.459157718", 22.459157718),
        ("EV-E-09", "e^pi-pi", "19.999099979", 19.999099979),
        ("EV-E-12", "(1+1/1000)^1000", "2.716923932", 2.716923932),
    ]
    plain_decimal = re.compile(r"-?\d+(\.\d+)?([eE][+-]?\d+)?")
    with TestClient(app) as client:
        for case_id, expression, frozen, reference in references:
            assert frozen in _row(case_id), case_id
            payload = _evaluate(client, expression)
            # Protocolo, regla 2: una salida que solo imprima el decimal no
            # certifica la fila; la forma exacta debe conservarse.
            assert not plain_decimal.fullmatch(payload["result_text"].strip()), (
                case_id,
                payload,
            )
            assert abs(payload["result_approx"] - reference) <= 5e-10, (expression, payload)

        # EV-E-11: the exact form exp(100) is kept; the reference is relative
        # and also rounded to nine decimals, hence the same 5e-10 tolerance.
        assert "2.688117142" in _row("EV-E-11")
        payload = _evaluate(client, "e^100")
        assert "exp(" in payload["result_text"], payload
        assert abs(payload["result_approx"] / 1e43 - 2.688117142) <= 5e-10, payload


def test_ev_e10_sum_of_logs_is_exact_six():
    assert "`6`" in _row("EV-E-10")
    with TestClient(app) as client:
        payload = _evaluate(client, "e^(ln(2)+ln(3))")
    assert payload["result_text"] == "6", payload
    assert payload["result_approx"] == 6.0, payload


def test_ev_e13_complex_exponential_is_minus_one():
    with TestClient(app) as client:
        payload = _evaluate(client, "e^(I*pi)")
    assert sp.simplify(_value(payload) - (-1)) == 0, payload


def test_ev_e14_zero_to_zero_declared_convention():
    # The row admits "1 por convención declarada"; the convention is recorded
    # in qa/certification/MANUAL_CAPABILITY_GAPS.md.
    with TestClient(app) as client:
        payload = _evaluate(client, "0^0")
    assert sp.simplify(_value(payload) - 1) == 0, payload
