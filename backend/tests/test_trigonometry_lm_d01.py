"""Trigonometry LM-D-01: lim x->0 sin(x)/x = 1 from frozen matrix.

Scope: source row + phase2 compute_limit (certified path for limits).
/api/v1/evaluate does not recognize the symbol 'limit' (PARSE_ERROR); that is
out of this case's product scope and is not claimed here.
"""
import gzip
import math
from pathlib import Path

import sympy
from fastapi.testclient import TestClient

from app.main import app
from app.services.phase2_service import compute_limit

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/ejercicios_trigonometria.md.gz"
SAMPLES = (-0.1, -0.01, -0.001, 0.001, 0.01, 0.1)


def test_lm_d01_source_row_present_in_frozen_matrix():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    row = next(line for line in text.splitlines() if "LM-D-01" in line and "lim" in line)
    assert r"\lim_{x\to 0}\frac{\sin x}{x}" in row
    assert "`1`" in row


def test_lm_d01_compute_limit_returns_exact_1():
    result = compute_limit("sin(x)/x", "x", "0", "both")
    assert result.value == 1
    assert result.value == sympy.Integer(1)


def test_lm_d01_independent_samples_approach_1():
    for x in SAMPLES:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/evaluate",
                json={"expression": f"sin({x})/({x})"},
            )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body.get("success") is True, body
        actual = body.get("result_approx")
        assert actual is not None, body
        assert body.get("result_text"), body
        assert abs(float(actual) - math.sin(x) / x) < 1e-12
        assert abs(actual - 1.0) < 0.02


def test_lm_d01_limit_endpoint_if_present():
    """Prefer dedicated limit API when available; soft-skip if route missing."""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/limit",
            json={"expression": "sin(x)/x", "variable": "x", "point": "0", "direction": "both"},
        )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body.get("success") is True, body
    assert body.get("result_text") == "1", body
    assert body.get("result_latex") == "1", body
