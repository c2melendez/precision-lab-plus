"""Cross-product regression: equivalent reciprocal-square input forms."""
import pytest
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

FORMS = ['(1/x)^2', 'x^(-2)', '1/(x*x)', '1/(x)^2']

@pytest.mark.parametrize('expression', FORMS)
@pytest.mark.parametrize('lower,upper', [('-1','1'), ('1','-1')])
def test_pole_is_rejected(expression, lower, upper):
    with TestClient(app) as client:
        body = client.post('/api/v1/integral', json={'expression': expression, 'variable': 'x', 'lower_bound': lower, 'upper_bound': upper}).json()
    assert body['success'] is False
    assert body['error_code'] == 'DOMAIN_ERROR'

@pytest.mark.parametrize('expression', FORMS)
def test_finite_interval(expression):
    with TestClient(app) as client:
        body = client.post('/api/v1/integral', json={'expression': expression, 'variable': 'x', 'lower_bound': '1', 'upper_bound': '2'}).json()
    assert body['success'] is True
    assert float(sp.N(sp.sympify(body['result_text']))) == pytest.approx(0.5)
