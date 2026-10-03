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
    # Complejo tiene prioridad sobre "numérico": 2+3*I es numérico,
    # pero necesita las cuatro representaciones complejas.
    if expr.has(sympy.I):
        return ResultKind.COMPLEX
    if is_numeric:
        return ResultKind.NUMERIC
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


def complex_views(input_expr: sympy.Expr, value: sympy.Expr) -> List[ResultView]:
    """Cuatro representaciones para un único número complejo evaluado."""
    re_part, im_part = [sympy.simplify(part) for part in value.as_real_imag()]
    magnitude = sympy.simplify(sympy.Abs(value))
    angle = sympy.simplify(sympy.arg(value))
    binomial = sympy.simplify(re_part + sympy.I * im_part)

    return dedupe_views(
        [
            _view("original", "Original", input_expr, ResultKind.COMPLEX),
            _view("complex_binomial", "Binómica", binomial, ResultKind.COMPLEX),
            ResultView(
                key="complex_polar",
                label="Polar",
                latex=f"{sympy.latex(magnitude)}\\angle {sympy.latex(angle)}",
                kind=ResultKind.COMPLEX,
            ),
            ResultView(
                key="complex_trigonometric",
                label="Trigonométrica",
                latex=(
                    f"{sympy.latex(magnitude)}"
                    f"\\left(\\cos\\left({sympy.latex(angle)}\\right)"
                    f"+i\\sin\\left({sympy.latex(angle)}\\right)\\right)"
                ),
                kind=ResultKind.COMPLEX,
            ),
            ResultView(
                key="complex_exponential",
                label="Exponencial",
                latex=f"{sympy.latex(magnitude)}e^{{i({sympy.latex(angle)})}}",
                kind=ResultKind.COMPLEX,
            ),
        ]
    )


def equation_views(
    input_eq: sympy.Expr,
    variable: sympy.Symbol | None,
    solutions: list,
    result_type,
) -> List[ResultView]:
    """Original + Solución únicamente; raíces complejas no generan 4 vistas."""
    views = [
        ResultView(
            key="original",
            label="Original",
            latex=sympy.latex(input_eq),
            kind=ResultKind.EQUATION,
        )
    ]
    result_type_value = str(getattr(result_type, "value", result_type))
    if result_type_value == "identity":
        solution_latex = r"\text{Identidad: se cumple para todo valor admisible}"
    elif result_type_value == "contradiction":
        solution_latex = r"\varnothing"
    else:
        var_latex = sympy.latex(variable) if variable is not None else "x"
        pieces = [
            f"{var_latex}_{{{idx + 1}}}={solution.latex}"
            for idx, solution in enumerate(solutions)
        ]
        solution_latex = r",\ ".join(pieces) if pieces else r"\varnothing"
    views.append(
        ResultView(
            key="solution",
            label="Solución",
            latex=solution_latex,
            kind=ResultKind.EQUATION,
        )
    )
    return views
