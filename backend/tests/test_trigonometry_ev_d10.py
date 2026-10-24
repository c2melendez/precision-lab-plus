"""Trigonometry EV-D-10: cot(pi/2) = 0 over HTTP evaluate (ASCII channel).

The official matrix entry is LaTeX. Plus certifies the HTTP /evaluate path
using the ASCII witness cot(pi/2); raw LaTeX ingestion is not claimed here.
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
INPUT_ASCII = "cot(pi/2)"
EXPECTED = sp.Integer(0)


def test_ev_d10_source_row_present_and_frozen():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    row = next((line for line in text.splitlines() if "| EV-D-10 |" in line), "")
    assert row, "EV-D-10 row missing from frozen trigonometry matrix"
    assert r"\cot\left(\frac{\pi}{2}\right)" in row
    assert row.rstrip().endswith("| 0 |") or "| `0` |" in row


def test_ev_d10_cot_pi_over_2_http_ascii():
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": INPUT_ASCII})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    text = payload["result_text"]
    got = sp.sympify(text.replace("^", "**"))
    assert sp.simplify(got - EXPECTED) == 0
