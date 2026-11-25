import math
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.mark.parametrize('expression,lower,upper',[
 ('cot(x)','-1','1'),('cot(x)','0','1'),('cot(x)','1','-1'),
 ('sec(x)^3','1','2'),('sec(x)^3','2','1'),
 ('1/x^2','-1','1'),('1/x^2','1','-1'),('1/x^2','0','1'),
 ('1/x^3','-1','1'),
])
def test_divergent_integral_is_not_a_success(expression,lower,upper):
 with TestClient(app) as client:
  response=client.post('/api/v1/integral',json={'expression':expression,'variable':'x','lower_bound':lower,'upper_bound':upper})
 body=response.json()
 assert body['success'] is False
 assert body['error_code']=='DOMAIN_ERROR'

@pytest.mark.parametrize('expression,lower,upper,expected',[
 ('cot(x)','1','2',math.log(abs(math.sin(2)))-math.log(abs(math.sin(1)))),
 ('sec(x)^3','0','1',(1/math.cos(1)*math.tan(1)+math.log(1/math.cos(1)+math.tan(1)))/2),
 ('1/x^2','1','2',0.5),('1/x^2','2','1',-0.5),
])
def test_valid_finite_integral_remains_successful(expression,lower,upper,expected):
 with TestClient(app) as client:
  response=client.post('/api/v1/integral',json={'expression':expression,'variable':'x','lower_bound':lower,'upper_bound':upper})
 body=response.json()
 assert body['success'] is True
 import sympy as sp
 assert float(sp.N(sp.sympify(body['result_text']))) == pytest.approx(expected,rel=1e-7)


def test_unresolved_integral_keeps_its_warning():
 with TestClient(app) as client:
  response=client.post('/api/v1/integral',json={'expression':'csch(x)^2','variable':'x','lower_bound':'-1','upper_bound':'1'})
 body=response.json()
 assert 'Integral(' in body['result_text']
 assert any('sin resolver' in warning for warning in body['warnings'])
