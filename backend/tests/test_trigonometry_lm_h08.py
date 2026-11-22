import gzip
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.phase2_service import compute_limit


def test_original_row():
    text = gzip.decompress((Path(__file__).resolve().parents[2] / 'qa/certification/legacy_sources/ejercicios_trigonometria.md.gz').read_bytes()).decode()
    row = next(line for line in text.splitlines() if '| LM-H-08 |' in line)
    assert r'\lim_{x\to\infty}\frac{\cosh x}{\sinh x}' in row
    assert '`1`' in row


def test_service():
    assert compute_limit('cosh(x)/sinh(x)', 'x', 'oo', 'both').value == sp.S.One


def test_http():
    with TestClient(app) as client:
        response = client.post('/api/v1/limit', json={'expression': 'cosh(x)/sinh(x)', 'variable': 'x', 'point': 'oo', 'direction': 'both'})
    assert response.status_code == 200, response.text
    assert response.json()['success'], response.json()
    assert response.json()['result_text'] == '1'
