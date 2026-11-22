import gzip
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.phase2_service import compute_limit


def test_original_row():
    text = gzip.decompress((Path(__file__).resolve().parents[2] / 'qa/certification/legacy_sources/ejercicios_trigonometria.md.gz').read_bytes()).decode()
    row = next(line for line in text.splitlines() if '| LM-H-10 |' in line)
    assert r'\lim_{x\to 0^{+}}\coth x' in row
    assert r'+\infty' in row


def test_service():
    assert compute_limit('coth(x)', 'x', '0', 'right').value == sp.oo
    assert compute_limit('coth(x)', 'x', '0', 'left').value == -sp.oo


def test_http():
    with TestClient(app) as client:
        response = client.post('/api/v1/limit', json={'expression': 'coth(x)', 'variable': 'x', 'point': '0', 'direction': 'right'})
    assert response.status_code == 200, response.text
    assert response.json()['success'], response.json()
    assert response.json()['result_text'] == 'oo'
