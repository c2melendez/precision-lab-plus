import sympy
from app.services import parsing
from app.services.evaluate_service import evaluate

def exact(text: str):
    return sympy.simplify(parsing.parse_expression_tree(text, allow_equation=False))

def test_en_pn_01_decimal_addition_is_exact_rational():
    assert exact("0.1+0.2") == sympy.Rational(3, 10)

def test_en_pn_02_decimal_multiplication_is_exact():
    assert exact("0.1*3") == sympy.Rational(3, 10)

def test_en_pn_03_float_trap_435():
    assert exact("4.35*100") == 435

def test_en_pn_04_float_trap_1005():
    assert exact("1.005*1000") == 1005

def test_en_pn_05_decimal_power_exact():
    assert exact("1.1^2") == sympy.Rational(121, 100)

def test_en_pn_06_cancellation_exact_zero():
    assert exact("0.3-0.1-0.2") == 0

def test_en_pn_07_thirds_sum_exact_one():
    assert exact("1/3+1/3+1/3") == 1

def test_en_pn_08_integer_above_2pow53():
    assert exact("9007199254740993") == sympy.Integer(9007199254740993)

def test_en_pn_09_integer_arithmetic_above_2pow53():
    assert exact("9007199254740993+1") == sympy.Integer(9007199254740994)

def test_en_pn_10_twenty_digit_carry():
    assert exact("99999999999999999999+1") == sympy.Integer(100000000000000000000)

def test_en_pn_11_thirty_digit_literal():
    assert exact("123456789012345678901234567890") == sympy.Integer(123456789012345678901234567890)

def test_en_pn_12_long_decimal_payload():
    assert exact("0.1234567890123456789012345*10^25") == sympy.Integer(1234567890123456789012345)

def test_en_pn_13_decimal_equality_exact():
    left=exact("0.1+0.2")
    right=exact("0.3")
    assert left == right

def test_en_pn_14_sqrt_identity_exact():
    assert exact("sqrt(2)^2") == 2

def test_en_pn_18_extreme_exponent_cancellation():
    assert exact("10^400*10^-400") == 1

def test_en_pn_19_tiny_power_is_exact_nonzero():
    value=exact("2^-1074")
    assert value == sympy.Rational(1, 2**1074)
    assert value != 0

def test_en_pn_20_huge_integer_does_not_overflow_evaluate():
    result=evaluate("2^1024")
    assert result.expr == sympy.Integer(2)**1024
    assert len(str(result.expr)) == 309
    assert str(result.expr).startswith("17976931348623159")

# EN-PN-15..17 are intentionally left for explicit repeating-decimal syntax
# support/error-contract verification; they are requires_human/non-blocking.
