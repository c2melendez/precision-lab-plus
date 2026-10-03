"""Contrato S26 de clasificación y vistas de resultados.

Esta capa no reemplaza los motores matemáticos. Describe qué tipo de
resultado se obtuvo y qué representaciones puede mostrar la UI sin volver a
inferir semántica desde cadenas LaTeX.
"""

from __future__ import annotations

from typing import Iterable, List

import sympy

from app.schemas.responses import ResultKind, ResultView, Step


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


def _transformed_view(
    key: str,
    label: str,
    before: sympy.Expr,
    after: sympy.Expr,
    kind: ResultKind,
    rule: str,
) -> ResultView:
    step = Step(
        index=0,
        title=label,
        description=f"Se obtiene la forma {label.lower()} equivalente.",
        rule=rule,
        latex_before=sympy.latex(before),
        latex_after=sympy.latex(after),
    )
    return ResultView(
        key=key,
        label=label,
        latex=sympy.latex(after),
        kind=kind,
        steps=[step],
        has_detailed_steps=False,
    )


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

    Para expresiones trigonométricas, una reducción real por identidad se
    expone como vista Identidad y se deduplica si coincide con Resultado.
    """
    views = [_view("original", "Original", input_expr, kind)]
    if kind == ResultKind.TRIGONOMETRIC:
        identity_expr = sympy.trigsimp(input_expr)
        # La identidad debe aparecer cuando CAMBIA la representación
        # estructural, aunque ambas expresiones sean matemáticamente
        # equivalentes (que es justamente la definición de identidad).
        if sympy.srepr(identity_expr) != sympy.srepr(input_expr):
            views.append(_view("identity", "Identidad", identity_expr, kind))
    views.append(_view("result", result_label, result_expr, kind))
    return dedupe_views(views)



def _safe_transform(transform, expr: sympy.Expr) -> sympy.Expr | None:
    """Transformación opcional de vista.

    Una vista auxiliar nunca debe convertir un cálculo válido en error:
    si SymPy no puede producirla de forma segura, simplemente se omite.
    """
    try:
        transformed = transform(expr)
    except Exception:
        return None
    return transformed if isinstance(transformed, sympy.Expr) else None


def expression_views(
    input_expr: sympy.Expr,
    result_expr: sympy.Expr,
    kind: ResultKind,
) -> List[ResultView]:
    """Contrato completo de vistas para evaluación simbólica general."""
    views: List[ResultView] = [_view("original", "Original", input_expr, kind)]

    simplified = _safe_transform(sympy.simplify, input_expr)
    if simplified is not None:
        views.append(_transformed_view(
            "simplified", "Simplificada", input_expr, simplified, kind, "Simplify"
        ))

    # Las formas algebraicas siguen siendo útiles como representaciones
    # equivalentes en racionales/radicales/log-exp/trig siempre que cambien.
    factored = _safe_transform(sympy.factor, input_expr)
    if factored is not None:
        views.append(_transformed_view(
            "factored", "Factorizada", input_expr, factored, kind, "Factor"
        ))

    expanded = _safe_transform(sympy.expand, input_expr)
    if expanded is not None:
        views.append(_transformed_view(
            "expanded", "Expandida", input_expr, expanded, kind, "Expand"
        ))

    if kind == ResultKind.RATIONAL:
        rational_equiv = _safe_transform(sympy.cancel, input_expr)
        if rational_equiv is not None:
            views.append(_transformed_view(
                "identity", "Forma equivalente", input_expr, rational_equiv, kind, "Cancel"
            ))
    elif kind == ResultKind.RADICAL:
        radical_equiv = _safe_transform(sympy.radsimp, input_expr)
        if radical_equiv is not None:
            views.append(_transformed_view(
                "identity", "Forma equivalente", input_expr, radical_equiv, kind, "RadicalSimplify"
            ))
    elif kind == ResultKind.LOGARITHMIC:
        log_equiv = _safe_transform(lambda e: sympy.expand_log(e, force=False), input_expr)
        if log_equiv is not None:
            views.append(_transformed_view(
                "identity", "Forma equivalente", input_expr, log_equiv, kind, "LogExpand"
            ))
    elif kind == ResultKind.EXPONENTIAL:
        exp_equiv = _safe_transform(sympy.powsimp, input_expr)
        if exp_equiv is not None:
            views.append(_transformed_view(
                "identity", "Forma equivalente", input_expr, exp_equiv, kind, "PowerSimplify"
            ))
    elif kind == ResultKind.TRIGONOMETRIC:
        trig_equiv = _safe_transform(sympy.trigsimp, input_expr)
        if trig_equiv is not None:
            views.append(_transformed_view(
                "identity", "Identidad", input_expr, trig_equiv, kind, "TrigSimplify"
            ))

    views.append(_view("result", "Resultado", result_expr, kind))
    return dedupe_views(views)

def algebra_views(
    input_expr: sympy.Expr,
    result_expr: sympy.Expr,
    kind: ResultKind,
    operation: str,
    steps: List[Step] | None = None,
    has_detailed_steps: bool = False,
) -> List[ResultView]:
    key_label = {
        "simplify": ("simplified", "Simplificada"),
        "factor": ("factored", "Factorizada"),
        "expand": ("expanded", "Expandida"),
    }
    key, label = key_label[operation]
    transformed = ResultView(
        key=key,
        label=label,
        latex=sympy.latex(result_expr),
        kind=kind,
        steps=steps or [],
        has_detailed_steps=has_detailed_steps,
    )
    return dedupe_views(
        [
            _view("original", "Original", input_expr, kind),
            transformed,
        ]
    )


def complex_views(input_expr: sympy.Expr, value: sympy.Expr) -> List[ResultView]:
    """Cuatro representaciones para un único número complejo evaluado."""
    re_part, im_part = [sympy.simplify(part) for part in value.as_real_imag()]
    magnitude = sympy.simplify(sympy.Abs(value))
    angle = sympy.simplify(sympy.arg(value))
    binomial = sympy.simplify(re_part + sympy.I * im_part)

    # En complejos NO se deduplica Original contra Binómica: ambas vistas
    # tienen semántica distinta dentro del contrato aunque una entrada ya
    # venga escrita en forma binómica.
    return [
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
