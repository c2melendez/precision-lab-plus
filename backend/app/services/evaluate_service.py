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


def _safe_simplify_numeric(expr: sympy.Expr) -> sympy.Expr:
    """Simplifica resultados numéricos exactos sin expandir enteros enormes.

    Mantiene el AST y sus límites de complejidad como primera barrera. Esta
    segunda cota evita que un `simplify()` convierta potencias permitidas,
    pero gigantes, en enteros de miles de dígitos durante la serialización.
    """
    if not expr.is_number or sympy.count_ops(expr) > 50 or expr.has(sympy.factorial):
        return expr

    for node in sympy.preorder_traversal(expr):
        if not isinstance(node, sympy.Pow):
            continue
        base, exponent = node.args
        if exponent.is_Integer:
            power = abs(int(exponent))
            if base.is_Integer and abs(int(base)) > 1:
                # Cota conservadora de dígitos para una potencia entera.
                estimated_digits = len(str(abs(int(base)))) * power
                if estimated_digits > 1000:
                    return expr
            elif power > 1000:
                return expr
        elif exponent.is_rational is True:
            numerator_expr, denominator_expr = exponent.as_numer_denom()
            if not numerator_expr.is_Integer or not denominator_expr.is_Integer:
                return expr
            numerator = abs(int(numerator_expr))
            denominator = abs(int(denominator_expr))
            if denominator == 0 or numerator > 100 or denominator > 100:
                return expr
            if base.is_Integer and abs(int(base)) > 1:
                estimated_digits = len(str(abs(int(base)))) * numerator / denominator
                if estimated_digits > 1000:
                    return expr
        else:
            return expr

    try:
        simplified = sympy.simplify(expr)
    except (AttributeError, ZeroDivisionError, ValueError, OverflowError, TypeError):
        return expr

    if simplified.free_symbols or sympy.count_ops(simplified) > 100:
        return expr
    return simplified


def _reject_real_inverse_hyperbolic_boundary_values(expr: sympy.Expr) -> None:
    """Reject exact real boundary values where inverse hyperbolic functions diverge.

    SymPy's unevaluated atanh(1) can be reduced incorrectly by the generic
    simplify path in this application. Check these mathematical boundaries
    on the parsed AST before any simplification:
      atanh(±1), asech(0), acoth(±1).
    """
    boundary_values = {
        sympy.atanh: {sympy.S.NegativeOne, sympy.S.One},
        sympy.asech: {sympy.S.Zero},
        sympy.acoth: {sympy.S.NegativeOne, sympy.S.One},
    }
    for node in sympy.preorder_traversal(expr):
        invalid_arguments = boundary_values.get(node.func)
        if invalid_arguments is None or len(node.args) != 1:
            continue
        argument = node.args[0]
        if (
            argument.is_number
            and argument.is_real
            and argument in invalid_arguments
        ):
            raise DomainErrorResult(
                "El resultado no está definido en este dominio."
            )


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
        # Variables libres sin sustituir -> resultado simbólico (sección 6).
        return EvaluateResult(expr=expr, input_expr=input_expr, is_numeric=False)

    # Sin variables libres sin sustituir -> numérico (sección 6).
    # Verificar primero fronteras reales de funciones hiperbólicas
    # inversas; simplificar atanh(1) con SymPy puede borrar el polo.
    _reject_real_inverse_hyperbolic_boundary_values(expr)

    # La conversión desde el campo MathLive y el parser seguro conservan a
    # veces operaciones en forma no evaluada (2+3, x^(1/3) con x=27). Se
    # simplifica solo tras pasar el control AST y con una cota que evita
    # materializar resultados enteros enormes.
    expr = _safe_simplify_numeric(expr)

    # Fix (suite de regresión v1.1, caso E147: tan(pi/2) evaluate daba un
    # número finito gigante en vez de clasificarse como indefinido). El
    # parser preserva "pi/2" en forma exacta (Rational * pi, no un
    # Float), pero `expr.evalf()` no simplifica primero — numéricamente
    # aproxima tan(pi/2) sin darse cuenta de que es una asíntota exacta.
    # Un `simplify()` SÍ la resuelve a zoo exactamente (trabaja
    # simbólicamente), pero llamarlo en CADA evaluate (incluso para
    # expresiones que no tienen ninguna función trig) resultó demasiado
    # lento en la práctica (~decenas de veces más lento, tumbó el
    # servidor en la corrida de la suite). Se acota el chequeo caro a
    # los dos casos donde puede pasar esto: la expresión evalúa a un
    # número sospechosamente grande, o contiene una función trig directa
    # aplicada a algo que involucra pi (que es como se cuela un float en
    # vez de la forma exacta) — evalf() normal sigue siendo el camino
    # rápido para todo lo demás.
    # Para funciones trig directas evaluadas en argumentos exactos con π,
    # resolver primero el posible polo simbólico. Esto evita que expresiones
    # como sec(pi/2) entren en evalf() antes de que SymPy las reduzca a zoo.
    exact_trig_with_pi = expr.has(sympy.tan, sympy.sec, sympy.csc, sympy.cot) and expr.has(sympy.pi)
    if exact_trig_with_pi:
        try:
            simplified_pole = sympy.simplify(expr)
        except (AttributeError, ZeroDivisionError, ValueError, OverflowError):
            simplified_pole = None
        if simplified_pole is not None and simplified_pole.has(
            sympy.zoo, sympy.oo, -sympy.oo, sympy.nan
        ):
            raise DomainErrorResult("El resultado no está definido en este dominio.")

    try:
        numeric_value = expr.evalf()
    except (AttributeError, ZeroDivisionError, ValueError, OverflowError) as exc:
        raise DomainErrorResult("El resultado no está definido en este dominio.") from exc
    needs_pole_check = (
        numeric_value.is_number
        and numeric_value.is_finite is not False
        and not numeric_value.has(sympy.zoo, sympy.oo, -sympy.oo, sympy.nan)
        and exact_trig_with_pi
    )
    if needs_pole_check:
        try:
            got_big = abs(complex(numeric_value)) > 1e8
        except Exception:
            got_big = False
        if got_big and sympy.simplify(expr).has(sympy.zoo, sympy.oo, -sympy.oo, sympy.nan):
            raise DomainErrorResult("El resultado no está definido en este dominio.")
    if numeric_value.has(sympy.zoo, sympy.oo, -sympy.oo, sympy.nan):
        raise DomainErrorResult("El resultado no está definido en este dominio.")

    approx = float(numeric_value) if numeric_value.is_real else None

    return EvaluateResult(expr=expr, input_expr=input_expr, is_numeric=True, approx_value=approx)
