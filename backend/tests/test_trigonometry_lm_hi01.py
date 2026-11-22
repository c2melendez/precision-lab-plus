import gzip
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.phase2_service import compute_limit


def test_original_row():
    text = gzip.decompress((Path(__file__).resolve().parents[2] / 'qa/certification/legacy_sources/ejercicios_trigonometria.md.gz').read_bytes()).decode()
    row = next(line for line in text.splitlines() if '| LM-HI-01 |' in line)
    assert r'\lim_{x\to 0}\frac{\operatorname{arsinh} x}{x}' in row
    assert '`1`' in row


def test_service_sides():
    for direction in ('both', 'left', 'right'):
        assert compute_limit('asinh(x)/x', 'x', '0', direction).value == sp.S.One


def test_http():
    with TestClient(app) as client:
        response = client.post('/api/v1/limit', json={'expression': 'asinh(x)/x', 'variable': 'x', 'point': '0', 'direction': 'both'})
    assert response.status_code == 200, response.text
    assert response.json()['success'], response.json()
    assert response.json()['result_text'] == '1'
