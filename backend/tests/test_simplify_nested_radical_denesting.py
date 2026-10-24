"""Desanidación general de radicales numéricos anidados en /simplify.

Cubre la familia sqrt(a ± sqrt(b)) más allá del caso auditado AS-RAT-07, y
verifica que las expresiones sin forma desanidable o con variables no cambian.
"""

import pytest
import sympy as sp

from app.services.algebra_service import simplify_expression

DENESTED = [
    ("sqrt(2+sqrt(3))", sp.sqrt(6) / 2 + sp.sqrt(2) / 2),
    ("sqrt(3+sqrt(5))", sp.sqrt(10) / 2 + sp.sqrt(2) / 2),
    ("sqrt(5+2*sqrt(6))", sp.sqrt(2) + sp.sqrt(3)),
    ("sqrt(7-sqrt(13))", sp.sqrt(26) / 2 - sp.sqrt(2) / 2),
    ("sqrt(2-sqrt(3))", sp.sqrt(6) / 2 - sp.sqrt(2) / 2),
    ("sqrt(10+2*sqrt(21))", sp.sqrt(3) + sp.sqrt(7)),
    ("sqrt(7+4*sqrt(3))", sp.sqrt(3) + 2),
    ("sqrt(9+4*sqrt(5))", 2 + sp.sqrt(5)),
    ("sqrt(16-2*sqrt(15))", sp.sqrt(15) - 1),
    ("sqrt(6+sqrt(11))", sp.sqrt(22) / 2 + sp.sqrt(2) / 2),
    ("sqrt(2+sqrt(3))+1", 1 + sp.sqrt(6) / 2 + sp.sqrt(2) / 2),
    ("sqrt(2+sqrt(3))*sqrt(2)", 1 + sp.sqrt(3)),
]

UNCHANGED = [
    "sqrt(1+sqrt(2))",
    "sqrt(2+sqrt(2))",
    "sqrt(2*x+sqrt(3))",
    "sqrt(1-2*sqrt(2))",
]


@pytest.mark.parametrize("original, expected", DENESTED)
def test_constant_nested_radicals_are_denested(original, expected):
    result = simplify_expression(original).result_expr
    assert result == expected
    assert abs(complex(sp.N(result, 40)) - complex(sp.N(sp.sympify(original), 40))) < 1e-30


@pytest.mark.parametrize("original", UNCHANGED)
def test_non_denestable_or_symbolic_radicals_are_unchanged(original):
    expr = sp.sympify(original)
    assert simplify_expression(original).result_expr == sp.simplify(expr)
