import sympy as sp
from fastapi.testclient import TestClient
from app.main import app
from app.services.parsing import parse_inequality_tree
from app.services.phase2_service import compute_inequality

BOUND = sp.log(2+sp.sqrt(3))
EXPECTED = sp.Interval.open(-BOUND, BOUND)

def test_service():
    result=compute_inequality(parse_inequality_tree('cosh(x)<2'),'x')
    assert result.solution_set == sp.Interval.open(-sp.acosh(2), sp.acosh(2))
    assert sp.simplify(sp.acosh(2).rewrite(sp.log) - BOUND) == 0
    assert result.solution_set.contains(0) is sp.S.true
    assert result.solution_set.contains(sp.acosh(2)) is sp.S.false
    assert result.solution_set.contains(-sp.acosh(2)) is sp.S.false

def test_source_literal_http():
    with TestClient(app) as client:
        response=client.post('/api/v1/inequality',json={'inequality':r'\cosh x<2','variable':'x'})
    assert response.status_code==200
    body=response.json()
    assert body['success'],body
    assert body['result_text']==str(sp.Interval.open(-sp.acosh(2), sp.acosh(2)))
