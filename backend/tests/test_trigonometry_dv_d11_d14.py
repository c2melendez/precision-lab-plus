import gzip
from pathlib import Path
import pytest
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.derivative_service import compute_derivative

x = sp.Symbol('x')
CASES = [
    ('DV-D-11', 'sin(x)/(1+cos(x))', 1, r'\frac{1}{1+\cos x}', 1/(1+sp.cos(x))),
    ('DV-D-12', 'ln(sec(x)+tan(x))', 1, r'\sec x', 1/sp.cos(x)),
    ('DV-D-13', 'tan(x)', 2, r'2\sec^{2}x\tan x', 2*sp.sin(x)/sp.cos(x)**3),
    ('DV-D-14', 'tan(x)', 1, '`2`', 1/sp.cos(x)**2),
]


@pytest.mark.parametrize('case,expression,order,expected,oracle', CASES)
def test_matrix_and_service(case, expression, order, expected, oracle):
    path = Path(__file__).resolve().parents[2] / 'qa/certification/legacy_sources/ejercicios_trigonometria.md.gz'
    row = next(line for line in gzip.decompress(path.read_bytes()).decode().splitlines() if f'| {case} |' in line)
    assert expected in row
    actual = compute_derivative(expression, 'x', order).result_expr
    assert sp.trigsimp(actual - oracle) == 0
    if case == 'DV-D-14': assert sp.simplify(actual.subs(x, sp.pi/4)) == 2


@pytest.mark.parametrize('case,expression,order,expected,oracle', CASES)
def test_http(case, expression, order, expected, oracle):
    with TestClient(app) as client:
        response = client.post('/api/v1/derivative', json={'expression': expression, 'variable': 'x', 'order': order})
    assert response.status_code == 200, response.text
    assert response.json()['success'], response.json()
    actual = sp.sympify(response.json()['result_text'])
    assert sp.trigsimp(actual - oracle) == 0
    if case == 'DV-D-14': assert sp.simplify(actual.subs(x, sp.pi/4)) == 2
