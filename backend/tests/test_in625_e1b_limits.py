import sympy
from app.services.phase2_service import compute_limit

def test_en_ca_20_sinx_over_x():
    r=compute_limit("sin(x)/x","x","0","both")
    assert r.value == 1

def test_en_ca_22_right_limit_one_over_x():
    r=compute_limit("1/x","x","0","right")
    assert r.value == sympy.oo

def test_en_ca_23_left_limit_one_over_x():
    r=compute_limit("1/x","x","0","left")
    assert r.value == -sympy.oo

def test_en_ca_24_limit_at_infinity():
    r=compute_limit("1/x","x","oo","both")
    assert r.value == 0
