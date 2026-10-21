"""Trigonometry EV-D-06: cot(pi/4) = 1 over HTTP evaluate (ASCII channel).

The official matrix entry is LaTeX. Plus certifies the HTTP /evaluate path
using the ASCII witness cot(pi/4); raw LaTeX ingestion is not claimed here.
"""
from pathlib import Path
import gzip
import re

import sympy as sp
from fastapi.testclient import TestClient

from app.main import app

SOURCE_GZ = (
    Path(__file__).resolve().parents[2]
    / "qa/certification/legacy_sources/ejercicios_trigonometria.md.gz"
)
INPUT_ASCII = "cot(pi/4)"
EXPECTED = sp.Integer(1)


def test_ev_d06_source_row_present_and_frozen():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| EV-D-06 |" in text
    assert r"\cot\left(\frac{\pi}{4}\right)" in text
    assert re.search(r"\|\s*EV-D-06\s*\|[^\n]*\|\s*`?1`?\s*\|", text)


def test_ev_d06_cot_pi_over_4_http_ascii():
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": INPUT_ASCII})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    got = sp.sympify(payload["result_text"].replace("^", "**"))
    assert sp.simplify(got - EXPECTED) == 0
