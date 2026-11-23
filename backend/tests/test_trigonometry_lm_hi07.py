import gzip
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.phase2_service import compute_limit


def test_original_row():
    path = Path(__file__).resolve().parents[2] / 'qa/certification/legacy_sources/ejercicios_trigonometria.md.gz'
    row = next(line for line in gzip.decompress(path.read_bytes()).decode().splitlines() if '| LM-HI-07 |' in line)
    assert r'\lim_{x\to 1^{+}}\frac{\operatorname{arcosh} x}{\sqrt{x-1}}' in row
    assert r'\sqrt{2}' in row


def test_service():
    assert sp.simplify(compute_limit('acosh(x)/sqrt(x-1)', 'x', '1', 'right').value - sp.sqrt(2)) == 0


def test_http():
    with TestClient(app) as client:
        response = client.post('/api/v1/limit', json={'expression': 'acosh(x)/sqrt(x-1)', 'variable': 'x', 'point': '1', 'direction': 'right'})
    assert response.status_code == 200, response.text
    assert response.json()['success'], response.json()
    assert sp.sympify(response.json()['result_text']) == sp.sqrt(2)
