"""TR324 IT-D: numeric differentiation of service antiderivatives."""
import gzip
import math
import os
import subprocess
import sys
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

INVERSE_CASES = [
 ('IT-I-01','asin(x)', lambda x:math.asin(x), [-.8,-.3,.3,.8]),
 ('IT-I-02','acos(x)', lambda x:math.acos(x), [-.8,-.3,.3,.8]),
 ('IT-I-03','atan(x)', lambda x:math.atan(x), [-.8,-.3,.3,.8]),
 pytest.param('IT-I-04','acot(x)', lambda x:math.atan2(1,x), [-.8,-.3,.3,.8], marks=pytest.mark.xfail(reason='negative arccot branch differs; contract review required',strict=True)),
 pytest.param('IT-I-05','asec(x)', lambda x:math.acos(1/x), [1.2,1.5,2,3], marks=pytest.mark.xfail(reason='integral remains unresolved',strict=True)),
 pytest.param('IT-I-06','acsc(x)', lambda x:math.asin(1/x), [1.2,1.5,2,3], marks=pytest.mark.xfail(reason='integral remains unresolved',strict=True)),
 ('IT-I-07','x*atan(x)', lambda x:x*math.atan(x), [-.8,-.3,.3,.8]),
 ('IT-I-08','asin(x)/sqrt(1-x^2)', lambda x:math.asin(x)/math.sqrt(1-x*x), [-.8,-.3,.3,.8]),
 ('IT-I-09','1/(1+x^2)', lambda x:1/(1+x*x), [-.8,-.3,.3,.8]),
 ('IT-I-10','1/sqrt(1-x^2)', lambda x:1/math.sqrt(1-x*x), [-.8,-.3,.3,.8]),
 ('IT-I-11','1/(x*sqrt(x^2-1))', lambda x:1/(x*math.sqrt(x*x-1)), [1.2,1.5,2,3]),
]

@pytest.mark.parametrize('case,expression,oracle,points', INVERSE_CASES)
def test_inverse_antiderivative_numeric(case, expression, oracle, points):
    row = next(line for line in MATRIX.splitlines() if f'| {case} |' in line)
    assert len(row.split('|')) >= 4
    result = integrate_expression(expression, 'x')
    assert not result.antiderivative.has(sp.Integral)
    f = sp.lambdify(sp.Symbol('x'), result.antiderivative, modules='math')
    for x in points:
        h = 1e-6
        assert (f(x+h)-f(x-h))/(2*h) == pytest.approx(oracle(x), rel=1e-6, abs=1e-6), (case, x)

HYPERBOLIC_CASES = [
 ('IT-H-01','sinh(x)',lambda x:math.sinh(x)),
 ('IT-H-02','cosh(x)',lambda x:math.cosh(x)),
 ('IT-H-03','tanh(x)',lambda x:math.tanh(x)),
 pytest.param('IT-H-04','coth(x)',lambda x:1/math.tanh(x),marks=pytest.mark.xfail(reason='logarithm real branch requires review',strict=True)),
 ('IT-H-05','sech(x)^2',lambda x:1/math.cosh(x)**2),
 ('IT-H-06','csch(x)^2',lambda x:1/math.sinh(x)**2),
 ('IT-H-07','sech(x)',lambda x:1/math.cosh(x)),
 pytest.param('IT-H-08','csch(x)',lambda x:1/math.sinh(x),marks=pytest.mark.xfail(reason='negative real logarithm branch',strict=True)),
 ('IT-H-09','sech(x)*tanh(x)',lambda x:math.tanh(x)/math.cosh(x)),
 ('IT-H-10','csch(x)*coth(x)',lambda x:math.cosh(x)/math.sinh(x)**2),
 ('IT-H-11','sinh(x)^2',lambda x:math.sinh(x)**2),
 ('IT-H-12','cosh(x)^2',lambda x:math.cosh(x)**2),
 pytest.param('IT-H-13','tanh(x)^2',lambda x:math.tanh(x)**2,marks=pytest.mark.xfail(reason='complex logarithmic form requires real-branch review',strict=True)),
 ('IT-H-14','x*sinh(x)',lambda x:x*math.sinh(x)),
 ('IT-H-15','sinh(x)*cosh(x)',lambda x:math.sinh(x)*math.cosh(x)),
 ('IT-H-16','exp(x)*cosh(x)',lambda x:math.exp(x)*math.cosh(x)),
]

@pytest.mark.parametrize('case,expression,oracle', HYPERBOLIC_CASES)
def test_hyperbolic_antiderivative_numeric(case, expression, oracle):
    row = next(line for line in MATRIX.splitlines() if f'| {case} |' in line)
    assert len(row.split('|')) >= 4
    result = integrate_expression(expression, 'x')
    assert not result.antiderivative.has(sp.Integral)
    f = sp.lambdify(sp.Symbol('x'), result.antiderivative, modules='math')
    for x in (-1.1,-.6,.6,1.1):
        h = 1e-6
        assert (f(x+h)-f(x-h))/(2*h) == pytest.approx(oracle(x), rel=1e-6, abs=1e-6), (case, x)

def test_csch_squared_primitive_preserves_pole():
    x = sp.Symbol('x')
    result = integrate_expression('csch(x)^2', 'x').antiderivative
    assert result.subs(x, 0).is_finite is False
    assert sp.simplify(sp.diff(result, x) - sp.csch(x)**2) == 0

def test_csch_squared_crossing_pole_is_not_reported_as_resolved():
    result = integrate_expression('csch(x)^2', 'x', '-1', '1')
    assert result.definite_value.has(sp.Integral) or result.definite_value.is_finite is False
    if result.definite_value.has(sp.Integral):
        assert any('sin resolver' in warning for warning in result.warnings)

@pytest.mark.parametrize('expression,lower,upper,oracle', [
    ('sech(x)^2', '-1', '1', lambda: 2*math.tanh(1)),
    ('csch(x)^2', '1', '2', lambda: 1/math.tanh(1)-1/math.tanh(2)),
    ('csch(x)^2', '-2', '-1', lambda: 1/math.tanh(1)-1/math.tanh(2)),
])
def test_reciprocal_hyperbolic_definite_integrals(expression, lower, upper, oracle):
    result = integrate_expression(expression, 'x', lower, upper)
    assert result.is_definite
    assert float(sp.N(result.definite_value, 15)) == pytest.approx(oracle(), rel=1e-10, abs=1e-10)

INVERSE_HYPERBOLIC_CASES = [
 ('IT-HI-01','asinh(x)',lambda x:math.asinh(x),[-2,-.5,.5,2]),
 ('IT-HI-02','acosh(x)',lambda x:math.acosh(x),[1.2,1.5,2,3]),
 ('IT-HI-03','atanh(x)',lambda x:math.atanh(x),[-.8,-.3,.3,.8]),
 pytest.param('IT-HI-04','acoth(x)',lambda x:math.atanh(1/x),[-3,-2,2,3],marks=pytest.mark.xfail(reason='negative real logarithm branch requires review',strict=True)),
 ('IT-HI-05','asech(x)',lambda x:math.acosh(1/x),[.1,.3,.6,.9]),
 pytest.param('IT-HI-06','acsch(x)',lambda x:math.asinh(1/x),[-2,-1,-.5,-.2,.2,.5,1,2],marks=pytest.mark.xfail(reason='integral unresolved; both real branches require verification',strict=True)),
 ('IT-HI-07','1/sqrt(x^2+1)',lambda x:1/math.sqrt(x*x+1),[-2,-.5,.5,2]),
 ('IT-HI-08','1/sqrt(x^2-1)',lambda x:1/math.sqrt(x*x-1),[1.2,1.5,2,3]),
 pytest.param('IT-HI-09','1/(1-x^2)',lambda x:1/(1-x*x),[-.8,-.3,.3,.8],marks=pytest.mark.xfail(reason='complex logarithmic representation requires real-branch review',strict=True)),
 ('IT-HI-10','x*asinh(x)',lambda x:x*math.asinh(x),[-2,-.5,.5,2]),
]

INVERSE_HYPERBOLIC_SOURCE = {
 'IT-HI-01': (r'\operatorname{arsinh} x', r'x\operatorname{arsinh} x-\sqrt{x^{2}+1}+C'),
 'IT-HI-02': (r'\operatorname{arcosh} x', r'x\operatorname{arcosh} x-\sqrt{x^{2}-1}+C'),
 'IT-HI-03': (r'\operatorname{artanh} x', r'x\operatorname{artanh} x+\frac{1}{2}\ln\left(1-x^{2}\right)+C'),
 'IT-HI-04': (r'\operatorname{arcoth} x', r'x\operatorname{arcoth} x+\frac{1}{2}\ln\left(x^{2}-1\right)+C'),
 'IT-HI-05': (r'\operatorname{arsech} x', r'x\operatorname{arsech} x+\arcsin x+C'),
 'IT-HI-06': (r'\operatorname{arcsch} x', r'x\operatorname{arcsch} x+\operatorname{arsinh} x+C'),
 'IT-HI-07': (r'\frac{dx}{\sqrt{x^{2}+1}}', r'\operatorname{arsinh} x+C'),
 'IT-HI-08': (r'\frac{dx}{\sqrt{x^{2}-1}}', r'\operatorname{arcosh} x+C'),
 'IT-HI-09': (r'\frac{dx}{1-x^{2}}', r'\operatorname{artanh} x+C'),
 'IT-HI-10': (r'x\operatorname{arsinh} x', r'\frac{2x^{2}+1}{4}\operatorname{arsinh} x-\frac{x\sqrt{x^{2}+1}}{4}+C'),
}

@pytest.mark.parametrize('case,expected', list(INVERSE_HYPERBOLIC_SOURCE.items()))
def test_inverse_hyperbolic_source_anchor(case, expected):
    row = next(line for line in MATRIX.splitlines() if f'| {case} |' in line)
    fields = row.split('|')
    assert expected[0] in fields[2]
    assert expected[1] in fields[3]

@pytest.mark.parametrize('case,expression,oracle,points', INVERSE_HYPERBOLIC_CASES)
def test_inverse_hyperbolic_integral(case, expression, oracle, points):
    assert any(f'| {case} |' in row for row in MATRIX.splitlines())
    result = integrate_expression(expression, 'x')
    assert not result.antiderivative.has(sp.Integral)
    f = sp.lambdify(sp.Symbol('x'), result.antiderivative, modules='math')
    for x in points:
        h = 1e-6
        assert (f(x+h)-f(x-h))/(2*h) == pytest.approx(oracle(x), rel=1e-6, abs=1e-6), (case,x)

@pytest.mark.parametrize('expression, endpoint, expected', [
    ('acosh(x)', 1, 0),
    ('asech(x)', 1, sp.pi/2),
])
def test_inverse_hyperbolic_primitive_endpoint(expression, endpoint, expected):
    result = integrate_expression(expression, 'x').antiderivative
    assert sp.simplify(result.subs(sp.Symbol('x'), endpoint) - expected) == 0

@pytest.mark.parametrize('seed', ['1', '3', '8'])
def test_inverse_sqrt_primitive_is_stable_across_hash_seeds(seed):
    script = """import sympy as s
from app.services.integral_service import integrate_expression
x=s.Symbol('x')
r=integrate_expression('1/sqrt(x^2-1)','x').antiderivative
for point in (1.2, 2, 2+1j, 2-1j, -2+1j, -2-1j):
    got=complex(s.N(s.diff(r,x).subs(x,point), 15))
    expected=complex(s.N((1/s.sqrt(x*x-1)).subs(x,point), 15))
    assert abs(got-expected) < 1e-10, (point, got, expected, r)
"""
    env = {**os.environ, 'PYTHONHASHSEED': seed}
    result = subprocess.run([sys.executable, '-c', script], env=env, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
