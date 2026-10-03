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


def test_complex_views_have_four_representations():
    value = 2 + 3 * sp.I
    views = result_contract.complex_views(value, value)
    assert [view.key for view in views] == [
        "original",
        "complex_binomial",
        "complex_polar",
        "complex_trigonometric",
        "complex_exponential",
    ]


def test_equation_views_do_not_expand_complex_roots():
    x = sp.Symbol("x")
    equation = sp.Eq(x**2 + 1, 0)
    solutions = [
        type("S", (), {"latex": "i"})(),
        type("S", (), {"latex": "-i"})(),
    ]
    views = result_contract.equation_views(
        equation, x, solutions, "equation_solutions"
    )
    assert [view.key for view in views] == ["original", "solution"]
    assert "complex_polar" not in [view.key for view in views]
    assert "x_{1}=i" in views[1].latex
    assert "x_{2}=-i" in views[1].latex


def test_trig_identity_view_is_exposed():
    x = sp.Symbol("x")
    expr = sp.sin(x)**2 + sp.cos(x)**2
    views = result_contract.basic_views(expr, sp.Integer(1), ResultKind.TRIGONOMETRIC)
    assert "identity" in [view.key for view in views]


def test_expression_views_cover_symbolic_families():
    x = sp.Symbol("x")

    algebra_views = result_contract.expression_views(
        (x + 1)**2,
        sp.expand((x + 1)**2),
        ResultKind.ALGEBRAIC,
    )
    assert "original" in [view.key for view in algebra_views]
    assert any(view.key in {"simplified", "factored", "expanded"} for view in algebra_views)

    rational_expr = (x**2 - 1)/(x - 1)
    rational_views = result_contract.expression_views(
        rational_expr,
        sp.simplify(rational_expr),
        ResultKind.RATIONAL,
    )
    assert any(view.label == "Forma equivalente" for view in rational_views)

    log_expr = sp.log(x**2)
    log_views = result_contract.expression_views(
        log_expr,
        log_expr,
        ResultKind.LOGARITHMIC,
    )
    assert "original" in [view.key for view in log_views]

    trig_expr = sp.sin(x)**2 + sp.cos(x)**2
    trig_views = result_contract.expression_views(
        trig_expr,
        sp.Integer(1),
        ResultKind.TRIGONOMETRIC,
    )
    assert "identity" in [view.key for view in trig_views]
