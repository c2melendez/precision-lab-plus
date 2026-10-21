"""Trigonometry EV-D-12: tan(pi/2) is undefined and must report a clear domain error.

The official matrix row declares `indefinida (error claro)`. Plus certifies the
HTTP /evaluate path: undefined values return success=False with DOMAIN_ERROR,
never a silent numeric approximation.

AUD-SING-01 (avoidable-singularity audit): acot(0) must be exactly pi/2.
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


def test_ev_d12_source_row_present_and_declares_clear_error():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    row = next((line for line in text.splitlines() if "| EV-D-12 |" in line), "")
    assert row, "EV-D-12 row missing from frozen trigonometry matrix"
    assert r"\tan\left(\frac{\pi}{2}\right)" in row
    assert "indefinida" in row.lower()
    assert "error claro" in row.lower()


def test_ev_d12_tan_pi_over_2_reports_domain_error():
    with TestClient(app) as client:
        payload = _evaluate(client, "tan(pi/2)")
    assert payload["success"] is False, payload
    assert payload["error_code"] == "DOMAIN_ERROR", payload
    assert payload.get("result_text") in (None, ""), payload


def test_ev_d12_defined_tangent_values_still_pass():
    with TestClient(app) as client:
        payload = _evaluate(client, "tan(pi/4)")
    assert payload["success"] is True, payload
    assert sp.simplify(sp.sympify(payload["result_text"].replace("^", "**")) - sp.Integer(1)) == 0


def test_ev_d12_log_zero_reports_domain_error():
    with TestClient(app) as client:
        payload = _evaluate(client, "log(0)")
    assert payload["success"] is False, payload
    assert payload["error_code"] == "DOMAIN_ERROR", payload


def test_aud_sing_01_acot_zero_is_pi_over_2():
    with TestClient(app) as client:
        payload = _evaluate(client, "acot(0)")
    assert payload["success"] is True, payload
    got = sp.sympify(payload["result_text"].replace("^", "**"))
    assert sp.simplify(got - sp.pi / 2) == 0
