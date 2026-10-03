"""Contrato S26 de clasificación y vistas de resultados.

Esta capa no reemplaza los motores matemáticos. Describe qué tipo de
resultado se obtuvo y qué representaciones puede mostrar la UI sin volver a
inferir semántica desde cadenas LaTeX.
"""

from __future__ import annotations

from typing import Iterable, List

import sympy

from app.schemas.responses import ResultKind, ResultView


_TRIG_FUNCS = (
    sympy.sin, sympy.cos, sympy.tan, sympy.sec, sympy.csc, sympy.cot,
    sympy.asin, sympy.acos, sympy.atan,
    sympy.sinh, sympy.cosh, sympy.tanh, sympy.asinh, sympy.acosh, sympy.atanh,
)


def classify_expression(expr: sympy.Expr, *, is_numeric: bool = False) -> ResultKind:
    if is_numeric:
        return ResultKind.NUMERIC
    if expr.has(sympy.I):
        return ResultKind.COMPLEX
    if any(expr.has(fn) for fn in _TRIG_FUNCS):
        return ResultKind.TRIGONOMETRIC
    if expr.has(sympy.log):
        return ResultKind.LOGARITHMIC
    if expr.has(sympy.exp):
        return ResultKind.EXPONENTIAL
    if any(
        isinstance(node, sympy.Pow) and getattr(node.exp, "q", 1) != 1
        for node in sympy.preorder_traversal(expr)
    ):
        return ResultKind.RADICAL
    num, den = sympy.fraction(expr, exact=True)
    if den != 1 and (num.free_symbols or den.free_symbols):
        return ResultKind.RATIONAL
    if expr.free_symbols:
        return ResultKind.ALGEBRAIC
    return ResultKind.OTHER


def _view(key: str, label: str, expr: sympy.Expr, kind: ResultKind) -> ResultView:
    return ResultView(key=key, label=label, latex=sympy.latex(expr), kind=kind)


def dedupe_views(views: Iterable[ResultView]) -> List[ResultView]:
    result: List[ResultView] = []
    seen: set[str] = set()
    for view in views:
        normalized = "".join(view.latex.split())
        if normalized in seen:
            continue
        seen.add(normalized)
        result.append(view)
    return result


def basic_views(
    input_expr: sympy.Expr,
    result_expr: sympy.Expr,
    kind: ResultKind,
    result_label: str = "Resultado",
) -> List[ResultView]:
    """Vista base segura: interpretación original + resultado.

    Las transformaciones adicionales se añaden desde las rutas de álgebra
    donde ya existen presupuestos de complejidad y pasos verificados.
    """
    return dedupe_views(
        [
            _view("original", "Original", input_expr, kind),
            _view("result", result_label, result_expr, kind),
        ]
    )


def algebra_views(
    input_expr: sympy.Expr,
    result_expr: sympy.Expr,
    kind: ResultKind,
    operation: str,
) -> List[ResultView]:
    key_label = {
        "simplify": ("simplified", "Simplificada"),
        "factor": ("factored", "Factorizada"),
        "expand": ("expanded", "Expandida"),
    }
    key, label = key_label[operation]
    return dedupe_views(
        [
            _view("original", "Original", input_expr, kind),
            _view(key, label, result_expr, kind),
        ]
    )
