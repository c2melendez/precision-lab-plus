"""TR324 IT-D: numeric differentiation of service antiderivatives."""
import gzip
import math
from pathlib import Path
import pytest
import sympy as sp
from app.services.integral_service import integrate_expression

MATRIX = gzip.decompress((Path(__file__).resolve().parents[2] / 'qa/certification/legacy_sources/ejercicios_trigonometria.md.gz').read_bytes()).decode()
CASES = [
 ('IT-D-01','sin(x)',lambda x:math.sin(x)),
 ('IT-D-02','cos(x)',lambda x:math.cos(x)),
 ('IT-D-03','sec(x)^2',lambda x:1/math.cos(x)**2),
 ('IT-D-04','csc(x)^2',lambda x:1/math.sin(x)**2),
 ('IT-D-05','sec(x)*tan(x)',lambda x:math.tan(x)/math.cos(x)),
 ('IT-D-06','csc(x)*cot(x)',lambda x:math.cos(x)/math.sin(x)**2),
 ('IT-D-07','tan(x)',lambda x:math.tan(x)),
 pytest.param('IT-D-08','cot(x)',lambda x:1/math.tan(x), marks=pytest.mark.xfail(reason='real negative branch returns log(sin(x)) without absolute value', strict=True)),
 ('IT-D-09','sec(x)',lambda x:1/math.cos(x)),
 pytest.param('IT-D-10','csc(x)',lambda x:1/math.sin(x), marks=pytest.mark.xfail(reason='real negative branch returns log of negative argument', strict=True)),
 ('IT-D-11','sin(x)^2',lambda x:math.sin(x)**2),
 ('IT-D-12','sin(x)^3',lambda x:math.sin(x)**3),
 ('IT-D-13','tan(x)^2',lambda x:math.tan(x)**2),
 pytest.param('IT-D-14','sec(x)^3',lambda x:1/math.cos(x)**3, marks=pytest.mark.xfail(reason='real antiderivative represented using complex logarithms', strict=True)),
 ('IT-D-15','x*cos(x)',lambda x:x*math.cos(x)),
 ('IT-D-16','exp(x)*sin(x)',lambda x:math.exp(x)*math.sin(x)),
 ('IT-D-17','sin(3*x)',lambda x:math.sin(3*x)),
 ('IT-D-18','cos(x)/(1+sin(x)^2)',lambda x:math.cos(x)/(1+math.sin(x)**2)),
]

@pytest.mark.parametrize('case,expression,oracle', CASES)
def test_antiderivative_numeric(case, expression, oracle):
    row = next(line for line in MATRIX.splitlines() if f'| {case} |' in line)
    assert len(row.split('|')) >= 4
    result = integrate_expression(expression, 'x')
    assert not result.antiderivative.has(sp.Integral)
    f = sp.lambdify(sp.Symbol('x'), result.antiderivative, modules='math')
    for x in (-1.1, -0.6, 0.6, 1.1):
        h = 1e-6
        numerical = (f(x+h)-f(x-h))/(2*h)
        assert numerical == pytest.approx(oracle(x), rel=1e-6, abs=1e-6), (case, x)
