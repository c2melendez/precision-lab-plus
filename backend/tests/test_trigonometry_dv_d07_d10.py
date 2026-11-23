import gzip
from pathlib import Path
import pytest
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.derivative_service import compute_derivative

x = sp.Symbol('x')
CASES = [
    ('DV-D-07', 'sin(x^2)', r'2x\cos\left(x^{2}\right)', 2*x*sp.cos(x**2)),
    ('DV-D-08', 'tan(3*x)', r'3\sec^{2}(3x)', 3/sp.cos(3*x)**2),
    ('DV-D-09', 'x*cos(x)', r'\cos x-x\sin x', sp.cos(x)-x*sp.sin(x)),
    ('DV-D-10', 'sin(2*x)^3', r'6\sin^{2}(2x)\cos(2x)', 6*sp.sin(2*x)**2*sp.cos(2*x)),
]


@pytest.mark.parametrize('case,expression,expected,oracle', CASES)
def test_matrix_and_service(case, expression, expected, oracle):
    path = Path(__file__).resolve().parents[2] / 'qa/certification/legacy_sources/ejercicios_trigonometria.md.gz'
    row = next(line for line in gzip.decompress(path.read_bytes()).decode().splitlines() if f'| {case} |' in line)
    assert expected in row
    assert sp.trigsimp(compute_derivative(expression, 'x', 1).result_expr - oracle) == 0


@pytest.mark.parametrize('case,expression,expected,oracle', CASES)
def test_http(case, expression, expected, oracle):
    with TestClient(app) as client:
        response = client.post('/api/v1/derivative', json={'expression': expression, 'variable': 'x', 'order': 1})
    assert response.status_code == 200, response.text
    assert response.json()['success'], response.json()
    assert sp.trigsimp(sp.sympify(response.json()['result_text']) - oracle) == 0
