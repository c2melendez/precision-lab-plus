"""Trigonometry EV-D-05: sec(pi/3) = 2 over HTTP evaluate (ASCII channel).

The official matrix entry is LaTeX. Plus certifies the HTTP /evaluate path
using the ASCII witness sec(pi/3); raw LaTeX ingestion is not claimed here.
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
INPUT_ASCII = "sec(pi/3)"
EXPECTED = sp.Integer(2)


def test_ev_d05_source_row_present_and_frozen():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| EV-D-05 |" in text
    assert r"\sec\left(\frac{\pi}{3}\right)" in text
    assert re.search(r"\|\s*EV-D-05\s*\|[^\n]*\|\s*`?2`?\s*\|", text)


def test_ev_d05_sec_pi_over_3_http_ascii():
    with TestClient(app) as client:
        response = client.post("/api/v1/evaluate", json={"expression": INPUT_ASCII})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True, payload
    got = sp.sympify(payload["result_text"].replace("^", "**"))
    assert sp.simplify(got - EXPECTED) == 0
