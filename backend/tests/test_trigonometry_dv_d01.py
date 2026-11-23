import gzip
from pathlib import Path
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.derivative_service import compute_derivative


def test_original_row():
    path = Path(__file__).resolve().parents[2] / 'qa/certification/legacy_sources/ejercicios_trigonometria.md.gz'
    row = next(line for line in gzip.decompress(path.read_bytes()).decode().splitlines() if '| DV-D-01 |' in line)
    assert r'\frac{d}{dx}\sin x' in row
    assert r'\cos x' in row


def test_service():
    assert sp.simplify(compute_derivative('sin(x)', 'x', 1).result_expr - sp.cos(sp.Symbol('x'))) == 0


def test_http():
    with TestClient(app) as client:
        response = client.post('/api/v1/derivative', json={'expression': 'sin(x)', 'variable': 'x', 'order': 1})
    assert response.status_code == 200, response.text
    assert response.json()['success'], response.json()
    assert sp.simplify(sp.sympify(response.json()['result_text']) - sp.cos(sp.Symbol('x'))) == 0
