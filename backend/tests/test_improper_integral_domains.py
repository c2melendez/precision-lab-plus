"""Improper integrals: divergent poles and integrable singularities."""
import math
import pytest
import sympy as sp
from fastapi.testclient import TestClient
from app.main import app

@pytest.mark.parametrize('expression', ['1/(x-1)^2', '1/(x-1)', '1/(x^2-1)', 'tan(x)^2'])
def test_divergent_interior_pole(expression):
    with TestClient(app) as client:
        body = client.post('/api/v1/integral', json={'expression':expression, 'variable':'x', 'lower_bound':'-2', 'upper_bound':'2'}).json()
    assert body['success'] is False
    assert body['error_code'] == 'DOMAIN_ERROR'

@pytest.mark.parametrize('expression,expected', [('1/(x^2+1)',2*math.atan(2)), ('1/sqrt(abs(x))',4*math.sqrt(2))])
def test_convergent_control(expression,expected):
    with TestClient(app) as client:
        body = client.post('/api/v1/integral', json={'expression':expression, 'variable':'x', 'lower_bound':'-2', 'upper_bound':'2'}).json()
    assert body['success'] is True
    assert float(sp.N(sp.sympify(body['result_text']))) == pytest.approx(expected, rel=1e-8)
