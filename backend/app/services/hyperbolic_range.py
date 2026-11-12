"""Narrow real-domain hyperbolic range contradiction helpers for frozen EC-H contracts."""
from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

import sympy

from app.schemas.responses import ResultType, Step

if TYPE_CHECKING:
    from app.services.solve_service import SolveResult


def hyperbolic_tangent_out_of_range_contradiction(
    eq: sympy.Eq, var: sympy.Symbol, angle_unit: str, warnings: List[str]
):
    """Reject tanh(x)=c with real |c|>=1, which has no real solution.

    For real x, |tanh(x)| < 1. The frozen EC-H-10 contract requires the empty
    real solution set for tanh(x)=2; the generic SymPy path returns complex
    artanh branches instead.
    """
    # Local import avoids circular dependency with solve_service.
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
