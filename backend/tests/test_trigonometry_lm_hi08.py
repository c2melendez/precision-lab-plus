import gzip
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.phase2_service import compute_limit


def test_original_row():
    path = Path(__file__).resolve().parents[2] / 'qa/certification/legacy_sources/ejercicios_trigonometria.md.gz'
    row = next(line for line in gzip.decompress(path.read_bytes()).decode().splitlines() if '| LM-HI-08 |' in line)
    assert r'\lim_{x\to\infty}\operatorname{arcoth} x' in row
    assert '`0`' in row


def test_service():
    assert compute_limit('acoth(x)', 'x', 'oo', 'both').value == sp.S.Zero


def test_http():
    with TestClient(app) as client:
        response = client.post('/api/v1/limit', json={'expression': 'acoth(x)', 'variable': 'x', 'point': 'oo', 'direction': 'both'})
    assert response.status_code == 200, response.text
    assert response.json()['success'], response.json()
    assert response.json()['result_text'] == '0'
