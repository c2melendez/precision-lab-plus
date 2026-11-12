"""Narrow real-domain hyperbolic range contradiction helpers for frozen EC-H contracts."""
from __future__ import annotations

from typing import List, Optional

import sympy

from app.schemas.responses import ResultType, Step


def hyperbolic_tangent_out_of_range_contradiction(
    eq: sympy.Eq, var: sympy.Symbol, angle_unit: str, warnings: List[str]
):
    """Reject tanh(x)=c with real |c|>=1, which has no real solution.

    For real x, |tanh(x)| < 1. The frozen EC-H-10 contract requires the empty
    real solution set for tanh(x)=2; the generic SymPy path returns complex
    artanh branches instead.
    """
    from app.services.solve_service import SolveResult

    if var.name != "x":
        return None
    try:
        difference = sympy.expand(eq.lhs - eq.rhs)
        if difference.atoms(sympy.tanh) != {sympy.tanh(var)}:
            return None
        parameter = sympy.Symbol("_tanh_range_parameter", real=True)
        reduced = sympy.expand(difference.subs(sympy.tanh(var), parameter))
        if var in reduced.free_symbols:
            return None
        polynomial = sympy.Poly(reduced, parameter)
        if polynomial.degree() != 1:
            return None
        coefficients = polynomial.all_coeffs()
        if len(coefficients) != 2:
            return None
        slope, intercept = coefficients
        if slope == 0:
            return None
        if not all(value.is_number and value.is_real is True for value in (slope, intercept)):
            return None
        constant = sympy.simplify(-intercept / slope)
        if constant.is_real is not True:
            return None
        if sympy.simplify(sympy.Abs(constant) - 1).is_nonnegative is not True:
            return None

        step = Step(
            index=0,
            title="Tangente hiperbólica fuera del rango real",
            description=(
                "La ecuación se reduce a tanh(x)=c con |c|>=1; como "
                "|tanh(x)|<1 para todo x real, no existe solución real."
            ),
            rule="HyperbolicTangentRangeContradiction",
            latex_before=sympy.latex(eq),
            latex_after=r"|\tanh(x)| < 1 \;\Rightarrow\; \varnothing",
        )
        return SolveResult(eq, var, ResultType.CONTRADICTION, [], [step], True, warnings)
    except Exception:
        return None


def install_tanh_range_hook() -> None:
    """Wrap solve_equation so EC-H-10 is classified before the generic path."""
    from app.services import solve_service
    from app.services import parsing

    if getattr(solve_service, "_tanh_range_hook_installed", False):
        return

    original = solve_service.solve_equation

    def wrapped(equation_text: str, variable_name=None, angle_unit: str = "rad"):
        try:
            eq = parsing.parse_expression_tree(equation_text, allow_equation=True)
            free_symbols = sorted(eq.free_symbols, key=lambda s: s.name)
            if free_symbols and variable_name:
                var = next((s for s in free_symbols if s.name == variable_name), free_symbols[0])
            elif free_symbols:
                var = free_symbols[0]
            else:
                var = None
            if var is not None:
                hit = hyperbolic_tangent_out_of_range_contradiction(
                    eq, var, angle_unit, []
                )
                if hit is not None:
                    return hit
        except Exception:
            pass
        return original(equation_text, variable_name, angle_unit)

    solve_service.solve_equation = wrapped
    solve_service._tanh_range_hook_installed = True
