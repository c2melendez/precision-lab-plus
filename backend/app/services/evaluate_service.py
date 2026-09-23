"""
app/services/evaluate_service.py — `/evaluate` (spec, secciones 3, 5, 6, 7).

`/evaluate`: sin variables libres sin sustituir -> numérico; con variables
libres sin sustituir -> simbólico (sección 6). `angle_unit` solo dentro de
argumentos de funciones trig DIRECTAS (`sin`,`cos`,`tan`,`sec`,`csc`,`cot`);
las inversas siempre en radianes (sección 3). `substitutions` deben parsear
a valores PURAMENTE numéricos (sin variables libres) — si no, `VALIDATION_ERROR`.

`/evaluate` no está en la lista de operaciones con procedimiento paso a paso
(sección 8, 8.2-8.6) — nunca genera `steps` detallados, siempre
`has_detailed_steps: false`.
"""

from dataclasses import dataclass
from typing import Dict, Optional

import sympy
from sympy import cos, cot, csc, pi, sec, sin, tan

from app.services import parsing

_DIRECT_TRIG_FUNCTIONS = (sin, cos, tan, sec, csc, cot)
_NONFINITE_MARKERS = (sympy.zoo, sympy.oo, -sympy.oo, sympy.nan)


class SubstitutionValidationError(ValueError):
    """Un valor (o nombre) de `substitutions` no cumple el contrato de la
    sección 5 — se traduce a `ErrorCode.VALIDATION_ERROR`."""


class DomainErrorResult(ValueError):
    """El resultado numérico final no está definido (NaN/infinito/
    indeterminado) — se traduce a `ErrorCode.DOMAIN_ERROR`."""


@dataclass
class EvaluateResult:
    expr: sympy.Expr
    input_expr: sympy.Expr
    is_numeric: bool
    approx_value: Optional[float] = None


def _validate_and_parse_substitutions(
    substitutions: Optional[Dict[str, str]],
) -> Dict[sympy.Symbol, sympy.Expr]:
    if not substitutions:
        return {}

    parsed: Dict[sympy.Symbol, sympy.Expr] = {}
    for name, raw_value in substitutions.items():
        try:
            candidates = parsing.extract_candidate_identifiers(name)
        except parsing.ParseSecurityError as exc:
            raise SubstitutionValidationError(
                f"Nombre de variable inválido en substitutions: '{name}' ({exc})"
            ) from exc
        if candidates != [name]:
            raise SubstitutionValidationError(
                f"Nombre de variable inválido en substitutions: '{name}'."
            )

        try:
            value_expr = parsing.parse_expression_tree(raw_value, allow_equation=False)
        except Exception as exc:
            raise SubstitutionValidationError(
                f"El valor de substitutions['{name}'] no es una expresión numérica "
                f"válida: {exc}"
            ) from exc

        if value_expr.free_symbols:
            free_names = sorted(s.name for s in value_expr.free_symbols)
            raise SubstitutionValidationError(
                f"substitutions['{name}'] debe ser puramente numérico "
                f"(contiene variables libres: {free_names})."
            )
        parsed[sympy.Symbol(name)] = value_expr

    return parsed


def _apply_degree_conversion(expr: sympy.Expr) -> sympy.Expr:
    """Convierte grados -> radianes SOLO dentro de argumentos de funciones
    trig directas (sección 3: "alcance limitado a funciones trig directas").

    Corrección del pendiente #7 (equivalente Full del pendiente #6 de
    Lite): si el argumento YA contiene π no se vuelve a multiplicar por
    π/180 — evita la doble conversión cuando el usuario usa la tecla °
    con angle_unit="deg" activo al mismo tiempo.
    """

    def _is_direct_trig(node: sympy.Basic) -> bool:
        return isinstance(node, _DIRECT_TRIG_FUNCTIONS)

    def _convert(node: sympy.Basic) -> sympy.Basic:
        if node.args[0].has(pi):
            return node
        return node.func(node.args[0] * pi / 180)

    return expr.replace(_is_direct_trig, _convert)


def _has_nonfinite(value: object) -> bool:
    """Detecta zoo/oo/nan sin permitir que una anomalía interna de SymPy
    escape como HTTP 500.

    Hallazgo S19: bajo el entorno instrumentado de mutmut, `sec(pi/2)`
    reprodujo de forma intermitente un AttributeError después de pasar la
    suite normal. Para una expresión numérica en un polo exacto, una falla
    de introspección durante `.has(...)` es semánticamente un resultado no
    representable y debe convertirse en DOMAIN_ERROR, nunca INTERNAL_ERROR.
    """
    try:
        return bool(value.has(*_NONFINITE_MARKERS))
    except (AttributeError, TypeError, ValueError, OverflowError) as exc:
        raise DomainErrorResult("El resultado no está definido en este dominio.") from exc


def evaluate(
    expression: str,
    angle_unit: str = "rad",
    substitutions: Optional[Dict[str, str]] = None,
) -> EvaluateResult:
    substitution_map = _validate_and_parse_substitutions(substitutions)

    input_expr = parsing.parse_expression_tree(expression, allow_equation=False)
    expr = input_expr

    if angle_unit == "deg":
        expr = _apply_degree_conversion(expr)

    if substitution_map:
        expr = expr.subs(substitution_map)

    if expr.free_symbols:
        return EvaluateResult(expr=expr, input_expr=input_expr, is_numeric=False)

    # Sin variables libres -> numérico. Los polos trigonométricos exactos
    # con π se simplifican primero para evitar que evalf() los aproxime como
    # números finitos gigantes. Toda la rama numérica se protege contra
    # AttributeError/TypeError internos de SymPy: esos fallos son dominio
    # no representable para el contrato público, no un 500.
    try:
        exact_trig_with_pi = (
            expr.has(sympy.tan, sympy.sec, sympy.csc, sympy.cot)
            and expr.has(sympy.pi)
        )

        if exact_trig_with_pi:
            simplified_pole = sympy.simplify(expr)
            if _has_nonfinite(simplified_pole):
                raise DomainErrorResult("El resultado no está definido en este dominio.")

        numeric_value = expr.evalf()

        if _has_nonfinite(numeric_value):
            raise DomainErrorResult("El resultado no está definido en este dominio.")

        needs_pole_check = (
            numeric_value.is_number
            and numeric_value.is_finite is not False
            and exact_trig_with_pi
        )
        if needs_pole_check:
            try:
                got_big = abs(complex(numeric_value)) > 1e8
            except (TypeError, ValueError, OverflowError):
                got_big = False

            if got_big:
                simplified_pole = sympy.simplify(expr)
                if _has_nonfinite(simplified_pole):
                    raise DomainErrorResult("El resultado no está definido en este dominio.")

        approx = float(numeric_value) if numeric_value.is_real else None
    except DomainErrorResult:
        raise
    except (AttributeError, ZeroDivisionError, ValueError, OverflowError, TypeError) as exc:
        raise DomainErrorResult("El resultado no está definido en este dominio.") from exc

    return EvaluateResult(expr=expr, input_expr=input_expr, is_numeric=True, approx_value=approx)
