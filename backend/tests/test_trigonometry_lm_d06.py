import gzip
from pathlib import Path

import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.phase2_service import compute_limit


def test_source():
    text = gzip.decompress((Path(__file__).resolve().parents[2] / 'qa/certification/legacy_sources/ejercicios_trigonometria.md.gz').read_bytes()).decode()
    row = next(line for line in text.splitlines() if '| LM-D-06 |' in line)
    assert r'\lim_{x\to 0}\frac{\sec x-1}{x^{2}}' in row
    assert r'\frac{1}{2}' in row


def test_service_and_sides():
    for direction in ('both', 'left', 'right'):
        assert compute_limit('(sec(x)-1)/x**2', 'x', '0', direction).value == sp.Rational(1, 2)


def test_http_limit():
    with TestClient(app) as client:
        response = client.post('/api/v1/limit', json={'expression': '(sec(x)-1)/x**2', 'variable': 'x', 'point': '0', 'direction': 'both'})
    assert response.status_code == 200, response.text
    assert response.json()['success'], response.json()
    assert response.json()['result_text'] == '1/2'
