"""Trigonometry LM-D-01: lim x->0 sin(x)/x = 1 from frozen matrix."""
import gzip
from pathlib import Path

import sympy
from fastapi.testclient import TestClient

from app.main import app
from app.services.phase2_service import compute_limit

SOURCE_GZ = Path(__file__).resolve().parents[2] / "qa/certification/legacy_sources/ejercicios_trigonometria.md.gz"


def test_lm_d01_source_row_present_in_frozen_matrix():
    text = gzip.decompress(SOURCE_GZ.read_bytes()).decode("utf-8")
    assert "| LM-D-01 |" in text or "|  LM-D-01  |" in text or any(
        line.startswith("| LM-D-01 |") or "| LM-D-01 |" in line for line in text.splitlines()
    )
    assert r"\lim_{x\to 0}\frac{\sin x}{x}" in text
    # Expected cell is `1`
    row = next(line for line in text.splitlines() if "LM-D-01" in line and "lim" in line)
    assert "`1`" in row


def test_lm_d01_compute_limit_returns_exact_1():
    result = compute_limit("sin(x)/x", "x", "0", "both")
    assert result.value == 1
    assert result.value == sympy.Integer(1)


def test_lm_d01_evaluate_endpoint_ascii_limit_form():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/evaluate",
            json={"expression": "limit(sin(x)/x, x, 0)"},
        )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body.get("success") is True, body
    text = str(body.get("result_text", "")).replace(" ", "")
    assert text in ("1", "1.0"), body


def test_lm_d01_limit_endpoint_if_present():
    """Prefer dedicated limit API when available; skip soft if route missing."""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/limit",
            json={"expression": "sin(x)/x", "variable": "x", "point": "0", "direction": "both"},
        )
    if response.status_code == 404:
        return  # route optional for this contract
    assert response.status_code == 200, response.text
    body = response.json()
    assert body.get("success") is True or body.get("value") in (1, "1", 1.0), body
