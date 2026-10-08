from app.services import parsing

def test_en_ca_26_finite_sum():
    assert parsing.parse_expression_tree("sum(k,k,1,10)", allow_equation=False) == 55

def test_en_ca_28_finite_square_sum():
    assert parsing.parse_expression_tree("sum(k^2,k,1,10)", allow_equation=False) == 385

def test_en_ca_30_finite_product():
    assert parsing.parse_expression_tree("product(k,k,1,5)", allow_equation=False) == 120
