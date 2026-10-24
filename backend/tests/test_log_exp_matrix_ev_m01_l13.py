"""Log/Exp matrix EV-M-01..13: mixed log, exp, radicals and polynomials.

Bilateral coverage for the mixed rows of matriz_log_exp_radicales. The
frozen matrix is LaTeX; this API evaluates the documented plain translation
of each row (same convention as EV-E and EV-R). Each test asserts that the
row exists in the frozen source and compares the engine output against the
exact value or the nine-decimal reference printed in that row.
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
# separately in test_ev_m_source_rows_present.
EXPRESSIONS = {
    "EV-M-01": "ln((e^6)^(1/3))",
    "EV-M-02": "e^(2*ln(3))",
    "EV-M-03": "log(sqrt(8), 2)",
    "EV-M-04": "f(x)=ln(x^2+1); f(sqrt(e-1))",
    "EV-M-05": "f(x)=(x^3+1)^(1/3); f(2)",
    "EV-M-06": "f(x)=x^2*e^(-x); f(2)",
    "EV-M-07": "f(x)=ln(x)/x; f(e)",
    "EV-M-08": "f(x)=x^x; f(2)",
    "EV-M-09": "sqrt(2)^sqrt(2)",
    "EV-M-10": "ln((1+sqrt(5))/2)",
    "EV-M-11": "((1+sqrt(5))/2)^2",
    "EV-M-12": "f(x)=sqrt(x^2); f(-3)",
    "EV-M-13": "f(x)=ln(x-sqrt(x^2-1))+ln(x+sqrt(x^2-1)); f(2)",
}


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


def test_ev_m_source_rows_present():
    for index in range(1, 14):
        case_id = f"EV-M-{index:02d}"
        assert _row(case_id), f"{case_id} row missing"


def test_ev_m_exact_values():
    exact = [
        ("EV-M-01", 2),
        ("EV-M-02", 9),
        ("EV-M-03", sp.Rational(3, 2)),
        ("EV-M-04", 1),
        ("EV-M-08", 4),
        ("EV-M-12", 3),
        ("EV-M-13", 0),
    ]
    with TestClient(app) as client:
        for case_id, expected in exact:
            payload = _evaluate(client, EXPRESSIONS[case_id])
            assert sp.simplify(_value(payload) - expected) == 0, (case_id, payload)


def test_ev_m_approximations():
    # (id, referencia congelada, valor): el oraculo del test debe aparecer
    # literalmente en la fila congelada de la matriz.
    references = [
        ("EV-M-05", "2.080083823", 2.080083823),
        ("EV-M-06", "0.541341133", 0.541341133),
        ("EV-M-07", "0.367879441", 0.367879441),
        ("EV-M-09", "1.632526919", 1.632526919),
        ("EV-M-10", "0.481211825", 0.481211825),
        ("EV-M-11", "2.618033989", 2.618033989),
    ]
    plain_decimal = re.compile(r"-?\d+(\.\d+)?([eE][+-]?\d+)?")
    with TestClient(app) as client:
        for case_id, frozen, reference in references:
            assert frozen in _row(case_id), case_id
            payload = _evaluate(client, EXPRESSIONS[case_id])
            # Protocolo, regla 2: una salida que solo imprima el decimal no
            # certifica la fila; la forma exacta debe conservarse.
            assert not plain_decimal.fullmatch(payload["result_text"].strip()), (
                case_id,
                payload,
            )
            assert abs(payload["result_approx"] - reference) <= 5e-10, (
                case_id,
                payload,
            )


def test_ev_m02_scaled_logarithm_identity():
    with TestClient(app) as client:
        assert _value(_evaluate(client, "e^(2*ln(3))")) == 9
        assert _value(_evaluate(client, "e^(-2*ln(3))")) == sp.Rational(1, 9)
        assert _value(_evaluate(client, "e^(ln(3))")) == 3


def test_ev_m04_definition_call_keeps_natural_log_and_balanced_argument():
    with TestClient(app) as client:
        payload = _evaluate(client, "f(x)=ln(x^2+1); f(sqrt(e-1))")
        assert payload["success"] is True, payload
        assert payload["result_text"] == "1", payload
        assert payload["result_approx"] == 1.0, payload
        # La base natural se conserva a través de la sustitución.
        assert _value(_evaluate(client, "f(x)=ln(x); f(e)")) == 1
        # log(x) conserva su semántica de base 10 (ln(x)/ln(10)).
        assert _value(_evaluate(client, "f(x)=log(x); f(100)")) == 2
        # La llamada de una variable sigue funcionando sin cambios.
        assert _value(_evaluate(client, "f(x)=x^2; f(3)")) == 9


def test_ev_m13_conjugate_log_sum_is_zero():
    with TestClient(app) as client:
        payload = _evaluate(client, EXPRESSIONS["EV-M-13"])
        assert payload["result_text"] == "0", payload
        assert payload["result_approx"] == 0.0, payload
        assert _value(_evaluate(client, "ln(2-sqrt(3))+ln(2+sqrt(3))")) == 0
        # Producto 9-5 = 4: la suma no es cero y SymPy la reduce a ln(4).
        assert _value(_evaluate(client, "ln(3-sqrt(5))+ln(3+sqrt(5))")) != 0
