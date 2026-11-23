import gzip
from pathlib import Path
import pytest
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.derivative_service import compute_derivative

x = sp.Symbol('x')
CASES = [
    ('DV-I-04', 'acot(x)', r'-\frac{1}{1+x^{2}}', -1/(1+x**2)),
    ('DV-I-05', 'asec(x)', r'\frac{1}{\lvert x\rvert\sqrt{x^{2}-1}}', 1/(sp.Abs(x)*sp.sqrt(x**2-1))),
    ('DV-I-06', 'acsc(x)', r'-\frac{1}{\lvert x\rvert\sqrt{x^{2}-1}}', -1/(sp.Abs(x)*sp.sqrt(x**2-1))),
]


@pytest.mark.parametrize('case,expression,expected,oracle', CASES)
def test_matrix_and_service(case, expression, expected, oracle):
    path = Path(__file__).resolve().parents[2] / 'qa/certification/legacy_sources/ejercicios_trigonometria.md.gz'
    row = next(line for line in gzip.decompress(path.read_bytes()).decode().splitlines() if f'| {case} |' in line)
    assert expected in row
    actual = compute_derivative(expression, 'x', 1).result_expr
    for value in [-2, 2]:
        assert sp.simplify(actual.subs(x, value) - oracle.subs(x, value)) == 0


@pytest.mark.parametrize('case,expression,expected,oracle', CASES)
def test_http(case, expression, expected, oracle):
    with TestClient(app) as client:
        response = client.post('/api/v1/derivative', json={'expression': expression, 'variable': 'x', 'order': 1})
    assert response.status_code == 200, response.text
    assert response.json()['success'], response.json()
    actual = sp.sympify(response.json()['result_text'])
    for value in [-2, 2]:
        assert sp.simplify(actual.subs(x, value) - oracle.subs(x, value)) == 0
