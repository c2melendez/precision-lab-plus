"""Trigonometry EV-I-12: arcsin(2)/arccos(2) outside the real domain.

The frozen matrix requires a clear error ("fuera del dominio real"). SymPy
returns a complex value, so the endpoint must reject the out-of-range numeric
form explicitly instead of echoing "asin(2)" as a valid result.
"""
from pathlib import Path
import gzip

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app

SOURCE_GZ = (
    Path(__file__).resolve().parents[2]
    / "qa/certification/legacy_sources/ejercicios_trigonometria.md.gz"
)


def _evaluate(client: TestClient, expression: str) -> dict:
    response = client.post("/api/v1/evaluate", json={"expression": expression})
    assert response.status_code == 200, response.text
    return response.json()


def test_ev_i12_source_row_present_and_requires_clear_error():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    row = next((line for line in text.splitlines() if "| EV-I-12 |" in line), "")
    assert row, "EV-I-12 row missing from frozen trigonometry matrix"
    assert r"\arcsin(2)" in row
    assert "fuera del dominio real" in row.lower()
    assert "error claro" in row.lower()


def test_ev_i12_out_of_domain_inputs_report_domain_error():
    for expression in ("asin(2)", "acos(2)", "asin(-2)"):
        with TestClient(app) as client:
            payload = _evaluate(client, expression)
        assert payload["success"] is False, (expression, payload)
        assert payload["error_code"] == "DOMAIN_ERROR", (expression, payload)


def test_ev_i12_in_domain_values_unchanged():
    with TestClient(app) as client:
        payload = _evaluate(client, "asin(1/2)")
        symbolic = _evaluate(client, "asin(x)")
    assert payload["success"] is True, payload
    assert sp.simplify(sp.sympify(payload["result_text"].replace("^", "**")) - sp.pi / 6) == 0
    assert symbolic["success"] is True, symbolic
    assert "asin(x)" in symbolic["result_text"].replace(" ", "")
