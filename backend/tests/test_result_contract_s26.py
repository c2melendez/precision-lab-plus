import sympy as sp

from app.schemas.responses import ResultKind
from app.services import result_contract


def test_classify_result_families():
    x = sp.Symbol("x")
    cases = [
        (sp.Integer(42), True, ResultKind.NUMERIC),
        (x**2 + 2*x + 1, False, ResultKind.ALGEBRAIC),
        ((x**2 - 1)/(x - 1), False, ResultKind.RATIONAL),
        (sp.sqrt(x + 1), False, ResultKind.RADICAL),
        (sp.log(x), False, ResultKind.LOGARITHMIC),
        (sp.exp(x), False, ResultKind.EXPONENTIAL),
        (sp.sin(x) + sp.cos(x), False, ResultKind.TRIGONOMETRIC),
        (2 + 3*sp.I, False, ResultKind.COMPLEX),
    ]
    for expr, numeric, expected in cases:
        assert result_contract.classify_expression(expr, is_numeric=numeric) == expected


def test_basic_views_keep_original_and_result_without_duplicates():
    x = sp.Symbol("x")
    views = result_contract.basic_views((x + 1)**2, x**2 + 2*x + 1, ResultKind.ALGEBRAIC)
    assert views[0].key == "original"
    assert views[0].label == "Original"
    assert len({view.latex for view in views}) == len(views)


def test_algebra_views_use_operation_specific_label():
    x = sp.Symbol("x")
    views = result_contract.algebra_views(
        x**2 - 1,
        (x - 1)*(x + 1),
        ResultKind.ALGEBRAIC,
        "factor",
    )
    assert [view.key for view in views] == ["original", "factored"]
    assert views[1].label == "Factorizada"
