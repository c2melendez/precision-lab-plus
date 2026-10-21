"""Log/Exp/Rad matrix EV-R-01..14: radicals.

Bilateral coverage for the radical rows of matriz_log_exp_radicales. The
matrix mixes integer roots, exact radical forms, two branch-convention rows
and one complex row, so each row is asserted against its documented oracle.

Channel note: Plus certifies this matrix on its ASCII/SymPy channel, except
the odd-index radical rows (EV-R-03/EV-R-05), whose contractual input is the
LaTeX radical notation that distinguishes the real odd root from the
principal complex branch. EV-R-14 keeps the principal branch for fractional
powers, as declared in MANUAL_CAPABILITY_GAPS.
"""
from pathlib import Path
import gzip

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


def test_ev_r_source_rows_present():
    for index in range(1, 15):
        case_id = f"EV-R-{index:02d}"
        assert _row(case_id), f"{case_id} row missing"


def test_ev_r_integer_roots():
    exact = [
        ("sqrt(16)", 4),
        ("27^(1/3)", 3),
        ("81^(1/4)", 3),
        ("2^(1/3)*4^(1/3)", 2),
        ("16^(3/4)", 8),
    ]
    with TestClient(app) as client:
        for expression, expected in exact:
            payload = _evaluate(client, expression)
            assert sp.simplify(_value(payload) - expected) == 0, (expression, payload)


def test_ev_r_odd_radicals_are_real_roots():
    # LaTeX radical notation with an odd index on a negative literal is the
    # real root, which is what the frozen rows EV-R-03 and EV-R-05 require.
    with TestClient(app) as client:
        cube = _evaluate(client, r"\sqrt[3]{-8}")
        fifth = _evaluate(client, r"\sqrt[5]{-32}")
    assert cube["result_text"] == "-2", cube
    assert fifth["result_text"] == "-2", fifth


def test_ev_r_exact_radical_forms():
    exact = [
        ("sqrt(12)", 2 * sp.sqrt(3)),
        ("sqrt(8)+sqrt(18)", 5 * sp.sqrt(2)),
        ("1/(sqrt(2)+1)", sp.sqrt(2) - 1),
        ("sqrt(3+2*sqrt(2))", 1 + sp.sqrt(2)),
        ("sqrt(5+2*sqrt(6))", sp.sqrt(2) + sp.sqrt(3)),
    ]
    with TestClient(app) as client:
        for expression, expected in exact:
            payload = _evaluate(client, expression)
            assert sp.simplify(_value(payload) - expected) == 0, (expression, payload)


def test_ev_r_oracles_anchored_to_frozen_rows():
    frozen = [
        ("EV-R-03", "-2"),
        ("EV-R-05", "-2"),
        ("EV-R-06", "2\\sqrt{3}"),
        ("EV-R-07", "5\\sqrt{2}"),
        ("EV-R-08", "\\sqrt{2}-1"),
        ("EV-R-09", "`2`"),
        ("EV-R-10", "`8`"),
        ("EV-R-11", "1+\\sqrt{2}"),
        ("EV-R-12", "\\sqrt{2}+\\sqrt{3}"),
    ]
    for case_id, reference in frozen:
        assert reference in _row(case_id), case_id


def test_ev_r13_declared_complex_branch():
    # The row admits "en C: 2i" only when the branch is declared; the
    # declaration is recorded in qa/certification/MANUAL_CAPABILITY_GAPS.md.
    with TestClient(app) as client:
        payload = _evaluate(client, "sqrt(-4)")
    assert sp.simplify(_value(payload) - 2 * sp.I) == 0, payload


def test_ev_r14_declared_principal_convention():
    # Declared convention: fractional powers of a negative base use the
    # principal branch (2*(-1)^(1/3) = 1 + sqrt(3)i), while odd-index radical
    # notation (EV-R-03/05) returns the real root.
    with TestClient(app) as client:
        payload = _evaluate(client, "(-8)^(1/3)")
    # SymPy keeps 2*(-1)^(1/3) unevaluated; expand_complex exposes the
    # principal value 1 + sqrt(3)i exactly.
    value = sp.expand_complex(_value(payload))
    assert sp.simplify(value - (1 + sp.sqrt(3) * sp.I)) == 0, payload
