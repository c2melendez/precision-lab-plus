import gzip
from pathlib import Path
import pytest
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.derivative_service import compute_derivative

x = sp.Symbol('x')
CASES = [
    ('DV-D-02', 'cos(x)', r'-\sin x', -sp.sin(x)),
    ('DV-D-03', 'tan(x)', r'\sec^{2}x', 1/sp.cos(x)**2),
    ('DV-D-04', 'csc(x)', r'-\csc x\cot x', -sp.cos(x)/sp.sin(x)**2),
    ('DV-D-05', 'sec(x)', r'\sec x\tan x', sp.sin(x)/sp.cos(x)**2),
    ('DV-D-06', 'cot(x)', r'-\csc^{2}x', -1/sp.sin(x)**2),
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
