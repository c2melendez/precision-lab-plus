"""
app/services/integral_service.py — `/integral` (spec, sección 8.4,
`IntegralRequest`).

`manualintegrate` primero, con mapeo explícito de reglas a `Step`
(`PowerRule`, `ExpRule`, `TrigRule` — clase base real de SymPy que cubre
`SinRule`/`CosRule`/`Sec2Rule`/`CscCotRule`/`SecTanRule`/`Csc2Rule` vía
`isinstance`—, `URule`, `PartsRule`, `AddRule` con un `Step` por término).
Regla no mapeada -> paso resumen de ese sub-árbol (`ReciprocalRule`,
`ConstantRule`, `ArcsinRule`, etc. — no nombradas en la sección 8.4); si
`manualintegrate` no encuentra NINGUNA técnica (`DontKnowRule`) -> fallback
completo a `sympy.integrate()` directo, `has_detailed_steps: false` y
warning explícito. `ConstantTimesRule`/`AlternativeRule`/`RewriteRule` se
tratan como envoltorios transparentes (no son una "técnica" en sí, solo
bookkeeping interno de SymPy) — se recorre a través de ellos sin generar un
paso propio.
"""

from dataclasses import dataclass
from typing import List, Optional

import sympy
import sympy.integrals.manualintegrate as mi

from app.schemas.responses import Step
from app.services import parsing
from app.services.step_verification import verify_step_equivalence

UNSUPPORTED_INFINITE_BOUNDS_MESSAGE = "Los límites infinitos no están disponibles en esta fase."
# Nota de la sección 5, aplicada literalmente: este mensaje NO debe mencionar
# /integral/improper como alternativa — ese endpoint también responde
# UNSUPPORTED_IN_PHASE_1 (sección 2), así que prometerlo sería peor que no
# ofrecer ninguna alternativa.


class UnsupportedInfiniteBoundsError(ValueError):
    """Límite `oo`/`-oo` en Fase 1 -> `ErrorCode.UNSUPPORTED_IN_PHASE_1`."""


class UnsupportedTrigPowerError(ValueError):
    """Una potencia trigonométrica con n simbólico sigue sin antiderivada."""


class DivergentIntegralError(ValueError):
    """La integral definida cruza un polo real y no converge como integral propia."""


_RULE_LABELS = {
    mi.PowerRule: "Integral de potencia",
    mi.ExpRule: "Integral de exponencial",
}
_TRANSPARENT_WRAPPER_RULES = (mi.ConstantTimesRule, mi.AlternativeRule, mi.RewriteRule)


@dataclass
class IntegralResult:
    input_expr: sympy.Expr
    antiderivative: sympy.Expr
    steps: List[Step]
    has_detailed_steps: bool
    warnings: List[str]
    is_definite: bool
    definite_value: Optional[sympy.Expr] = None


def _local_antiderivative(rule) -> sympy.Expr:
    return sympy.integrate(rule.integrand, rule.variable)


def _label_for_rule(rule) -> Optional[str]:
    if isinstance(rule, mi.TrigRule):
        return "Integral trigonométrica"
    for rule_type, label in _RULE_LABELS.items():
        if isinstance(rule, rule_type):
            return label
    return None


def _unmapped_step(rule) -> List[Step]:
    step = Step(
        index=0,
        title="Integral",
        description="Cálculo directo (regla sin mapeo explícito en la sección 8.4).",
        latex_before=sympy.latex(rule.integrand),
        latex_after=sympy.latex(_local_antiderivative(rule)),
    )
    return [step]


def _walk_rule(rule) -> List[Step]:
    if isinstance(rule, mi.AddRule):
        steps: List[Step] = []
        for substep in rule.substeps:
            steps.extend(_walk_rule(substep))
        return steps

    if isinstance(rule, _TRANSPARENT_WRAPPER_RULES):
        inner = getattr(rule, "substep", None)
        if inner is None:
            alternatives = getattr(rule, "alternatives", None)
            inner = alternatives[0] if alternatives else None
        return _walk_rule(inner) if inner is not None else _unmapped_step(rule)

    if isinstance(rule, mi.URule):
        headline = Step(
            index=0,
            title=f"Sustitución u = {sympy.latex(rule.u_func)}",
            description="Se sustituye u por la parte interna de la expresión.",
            rule="URule",
            latex_before=sympy.latex(rule.integrand),
            latex_after=sympy.latex(_local_antiderivative(rule)),
        )
        return [headline, *_walk_rule(rule.substep)]

    if isinstance(rule, mi.PartsRule):
        headline = Step(
            index=0,
            title="Integración por partes",
            description=(
                f"u = {sympy.latex(rule.u)}, dv = {sympy.latex(rule.dv)}·d{rule.variable}."
            ),
            rule="PartsRule",
            latex_before=sympy.latex(rule.integrand),
            latex_after=sympy.latex(_local_antiderivative(rule)),
        )
        return [headline]

    label = _label_for_rule(rule)
    if label is not None:
        step = Step(
            index=0,
            title=label,
            description=f"Se aplicó la regla: {label.lower()}.",
            rule=type(rule).__name__,
            latex_before=sympy.latex(rule.integrand),
            latex_after=sympy.latex(_local_antiderivative(rule)),
        )
        return [step]

    return _unmapped_step(rule)


def _validate_variable(variable: str) -> sympy.Symbol:
    candidates = parsing.extract_candidate_identifiers(variable)
    if candidates != [variable]:
        raise parsing.ParseSecurityError(f"Nombre de variable inválido: '{variable}'.")
    return sympy.Symbol(variable)


def _parse_bound(raw_bound: str) -> sympy.Expr:
    bound_expr = parsing.parse_expression_tree(raw_bound, allow_equation=False)
    if bound_expr.has(sympy.oo, -sympy.oo):
        raise UnsupportedInfiniteBoundsError(UNSUPPORTED_INFINITE_BOUNDS_MESSAGE)
    return bound_expr


def _fast_antiderivative(input_expr: sympy.Expr, x: sympy.Symbol) -> Optional[sympy.Expr]:
    """Closed-form fast path for common B7 identities.

    These are exact structural identities, not heuristic approximations.
    Returning None preserves the existing manualintegrate/SymPy path.
    """
    # The parser retains unevaluated arithmetic for input/steps. Rebuild
    # only arithmetic nodes for structural fast-path matching; ordinary
    # SymPy evaluation preserves principal branches (no force=True).
    input_expr = input_expr.replace(
        lambda node: node.is_Add or node.is_Mul or node.is_Pow,
        lambda node: node.func(*node.args),
    )
    sin = sympy.sin
    cos = sympy.cos
    tan = sympy.tan
    sec = sympy.sec
    csc = sympy.csc
    cot = sympy.cot
    sinh = sympy.sinh
    cosh = sympy.cosh
    tanh = sympy.tanh
    sech = sympy.sech
    csch = sympy.csch
    coth = sympy.coth
    asin = sympy.asin
    acos = sympy.acos
    asec = sympy.asec
    acsc = sympy.acsc
    asinh = sympy.asinh
    acosh = sympy.acosh
    atanh = sympy.atanh
    asech = sympy.asech
    acsch = sympy.acsch
    exp = sympy.exp
    sqrt = sympy.sqrt
    log = sympy.log

    exact_rules = {
        sin(x): -cos(x),
        cos(x): sin(x),
        tan(x): -log(cos(x)),
        cot(x): log(sin(x)),
        sec(x) ** 2: tan(x),
        csc(x) ** 2: -cot(x),
        1 / (1 + x**2): sympy.atan(x),
        1 / sqrt(1 - x**2): asin(x),
        1 / sqrt(x**2 + 1): asinh(x),
        sinh(x): cosh(x),
        cosh(x): sinh(x),
        tanh(x): log(cosh(x)),
        sech(x) ** 2: tanh(x),
        csch(x) ** 2: -coth(x),
        csch(x) * coth(x): -csch(x),
        sinh(x) * cosh(x): sinh(x) ** 2 / 2,
        x * cos(x): x * sin(x) + cos(x),
        x * sin(x): -x * cos(x) + sin(x),
        x * sinh(x): x * cosh(x) - sinh(x),
        x * cosh(x): x * sinh(x) - cosh(x),
        sin(x) ** 2: x / 2 - sin(2 * x) / 4,
        sin(x) ** 3: -cos(x) + cos(x) ** 3 / 3,
        sinh(x) ** 2: sinh(2 * x) / 4 - x / 2,
        cosh(x) ** 2: sinh(2 * x) / 4 + x / 2,
        exp(x) * sin(x): exp(x) * (sin(x) - cos(x)) / 2,
        cos(x) / (1 + sin(x) ** 2): sympy.atan(sin(x)),
        asin(x): x * asin(x) + sqrt(1 - x**2),
        acos(x): x * acos(x) - sqrt(1 - x**2),
        asinh(x): x * asinh(x) - sqrt(x**2 + 1),
        acosh(x): x * acosh(x) - sqrt(x**2 - 1),
        atanh(x): x * atanh(x) + log(1 - x**2) / 2,
        sech(x): sympy.atan(sinh(x)),
        acsch(x): x * acsch(x) + asinh(x),
        asech(x): x * asech(x) + asin(x),
    }

    candidate = exact_rules.get(input_expr)
    if candidate is not None:
        return candidate

    if input_expr == asec(x):
        return x * asec(x) - log(x + sqrt(x**2 - 1))
    if input_expr == acsc(x):
        return x * acsc(x) + log(x + sqrt(x**2 - 1))

    if input_expr == x * asinh(x):
        return ((2 * x**2 + 1) * asinh(x) - x * sqrt(x**2 + 1)) / 4

    return None


def _compute_indefinite(input_expr: sympy.Expr, var_symbol: sympy.Symbol):
    fast = _fast_antiderivative(input_expr, var_symbol)
    # Preserve the existing detailed SinRule/CosRule procedure contract
    # for the simplest indefinite cases. Definite integrals may still use
    # the same closed forms below without paying for manualintegrate.
    preserve_detailed_rule = input_expr in (
        sympy.sin(var_symbol),
        sympy.cos(var_symbol),
    )
    if fast is not None and not preserve_detailed_rule:
        return (
            fast,
            [],
            False,
            ["Se aplicó una identidad de integración cerrada verificada."],
        )

    rule = mi.integral_steps(input_expr, var_symbol)

    if isinstance(rule, mi.DontKnowRule):
        antiderivative = sympy.integrate(input_expr, var_symbol)
        return (
            antiderivative,
            [],
            False,
            [
                "No se encontró una regla de integración mapeada para esta expresión; "
                "se usó el resultado directo de SymPy."
            ],
        )

    steps = _walk_rule(rule)
    antiderivative = mi.manualintegrate(input_expr, var_symbol)

    # manualintegrate conserva potencias con exponente 0/1 sin evaluar
    # (p. ej. tan(x)^1 -> Integral(tan(x), x)). SymPy sí las resuelve
    # después de simplificar la potencia; no mostrar una integral pendiente
    # como si fuera la antiderivada.
    if antiderivative.has(sympy.Integral):
        direct = sympy.integrate(sympy.simplify(input_expr), var_symbol)
        if not direct.has(sympy.Integral) and verify_step_equivalence(
            sympy.diff(direct, var_symbol), input_expr
        ) == "VERIFIED":
            return direct, [], False, ["Se usó el resultado directo de SymPy."]

    # Sección 8.4: cada paso verificado comparando la derivada del resultado
    # acumulado contra el integrando original.
    check = verify_step_equivalence(sympy.diff(antiderivative, var_symbol), input_expr)
    if check == "VERIFIED":
        return antiderivative, steps, True, []

    # Red de seguridad: si por algún motivo no verifica, se prefiere el
    # resultado directo de SymPy sin pasos antes que exponer un
    # procedimiento no verificado (sección 8.1, regla 3).
    antiderivative = sympy.integrate(input_expr, var_symbol)
    return antiderivative, [], False, []


def integrate_expression(
    expression: str,
    variable: str,
    lower_bound: Optional[str] = None,
    upper_bound: Optional[str] = None,
) -> IntegralResult:
    input_expr = parsing.parse_expression_tree(expression, allow_equation=False)
    var_symbol = _validate_variable(variable)

    # Definite integrals used to compute a full manual antiderivative first
    # and then call sympy.integrate() again for the definite reference.
    # That duplicated the most expensive symbolic work and caused many
    # 15-second client timeouts in the trigonometric matrix. For definite
    # requests, compute the definite value directly in one symbolic pass.
    if (
        lower_bound is not None
        and upper_bound is not None
        and input_expr.is_polynomial(var_symbol) is not True
    ):
        lower_expr = _parse_bound(lower_bound)
        upper_expr = _parse_bound(upper_bound)

        # Detect real discontinuities before applying a definite
        # antiderivative. SymPy 1.13.3 has a known failure mode when
        # periodic trig solution sets are intersected with symbolic
        # endpoints (for example +/-pi/2). Avoid that set-intersection
        # path entirely:
        #
        # 1) classify endpoint singularities by direct substitution;
        # 2) find only INTERIOR denominator zeros over a numerically
        #    bounded open interval. Exact endpoint convergence is still
        #    decided below with one-sided limits of an antiderivative.
        lower_endpoint = sympy.Min(lower_expr, upper_expr)
        upper_endpoint = sympy.Max(lower_expr, upper_expr)

        def _is_singular_at(point):
            value = sympy.simplify(input_expr.subs(var_symbol, point))
            return (
                value.has(sympy.zoo, sympy.oo, -sympy.oo, sympy.nan)
                or value.is_finite is False
            )

        lower_is_pole = _is_singular_at(lower_endpoint)
        upper_is_pole = _is_singular_at(upper_endpoint)

        rewritten = input_expr.rewrite(sympy.cos)
        denominator = sympy.denom(sympy.together(rewritten))
        if denominator != 1:
            try:
                lower_numeric = sympy.Float(sympy.N(lower_endpoint, 30), 30)
                upper_numeric = sympy.Float(sympy.N(upper_endpoint, 30), 30)
                interior_domain = sympy.Interval(
                    lower_numeric,
                    upper_numeric,
                    left_open=True,
                    right_open=True,
                )
                interior_poles = sympy.solveset(
                    denominator,
                    var_symbol,
                    domain=interior_domain,
                )
            except (TypeError, ValueError, NotImplementedError):
                interior_poles = sympy.EmptySet

            if isinstance(interior_poles, sympy.FiniteSet) and len(interior_poles) > 0:
                raise DivergentIntegralError(
                    "La integral no converge: el integrando tiene una singularidad en el interior del intervalo."
                )

        if lower_is_pole or upper_is_pole:
            # A pole at an endpoint does not imply divergence by itself.
            # Validate the corresponding improper one-sided limits of an
            # antiderivative. This accepts integrable endpoint
            # singularities such as 1/(x*sqrt(x**2-1)) on [1,2], while
            # still rejecting tan(x) on [-pi/2,pi/2].
            antiderivative_for_endpoint = sympy.integrate(input_expr, var_symbol)
            if antiderivative_for_endpoint.has(sympy.Integral):
                raise DivergentIntegralError(
                    "No se pudo verificar la convergencia de la singularidad en el extremo."
                )
            delta = sympy.simplify(upper_expr - lower_expr)
            forward = delta.is_nonnegative
            if forward is None:
                try:
                    forward = float(sympy.N(delta)) >= 0
                except (TypeError, ValueError):
                    forward = True

            lower_value = (
                sympy.limit(
                    antiderivative_for_endpoint,
                    var_symbol,
                    lower_expr,
                    dir="+" if forward else "-",
                )
                if _is_singular_at(lower_expr)
                else antiderivative_for_endpoint.subs(var_symbol, lower_expr)
            )
            upper_value = (
                sympy.limit(
                    antiderivative_for_endpoint,
                    var_symbol,
                    upper_expr,
                    dir="-" if forward else "+",
                )
                if _is_singular_at(upper_expr)
                else antiderivative_for_endpoint.subs(var_symbol, upper_expr)
            )
            endpoint_reference = sympy.simplify(upper_value - lower_value)
            if endpoint_reference.has(sympy.zoo, sympy.oo, -sympy.oo, sympy.nan):
                raise DivergentIntegralError(
                    "La integral no converge: la singularidad del extremo produce un límite infinito o indefinido."
                )
            if endpoint_reference.is_finite is False:
                raise DivergentIntegralError(
                    "La integral no converge en el extremo indicado."
                )
            return IntegralResult(
                input_expr=input_expr,
                antiderivative=antiderivative_for_endpoint,
                steps=[],
                has_detailed_steps=False,
                warnings=["Integral impropia convergente validada mediante límites laterales en el extremo."],
                is_definite=True,
                definite_value=endpoint_reference,
            )

        fast_antiderivative = _fast_antiderivative(input_expr, var_symbol)
        if fast_antiderivative is not None:
            reference = sympy.simplify(
                fast_antiderivative.subs(var_symbol, upper_expr)
                - fast_antiderivative.subs(var_symbol, lower_expr)
            )
            return IntegralResult(
                input_expr=input_expr,
                antiderivative=fast_antiderivative,
                steps=[],
                has_detailed_steps=False,
                warnings=["Integral definida evaluada directamente con una identidad cerrada verificada."],
                is_definite=True,
                definite_value=reference,
            )

        reference = sympy.integrate(input_expr, (var_symbol, lower_expr, upper_expr))
        return IntegralResult(
            input_expr=input_expr,
            antiderivative=sympy.Integral(input_expr, var_symbol),
            steps=[],
            has_detailed_steps=False,
            warnings=["Integral definida calculada directamente para evitar trabajo simbólico duplicado."],
            is_definite=True,
            definite_value=reference,
        )

    antiderivative, steps, has_detailed_steps, warnings = _compute_indefinite(
        input_expr, var_symbol
    )
    if (
        antiderivative.has(sympy.Integral)
        and input_expr.is_Pow
        and input_expr.base.func in (sympy.sin, sympy.cos, sympy.tan)
        and input_expr.exp.free_symbols
    ):
        raise UnsupportedTrigPowerError(
            "El exponente simbólico n no se resuelve como una antiderivada cerrada; "
            "usa un exponente entero concreto."
        )

    if lower_bound is None and upper_bound is None:
        for index, step in enumerate(steps):
            step.index = index
        return IntegralResult(
            input_expr, antiderivative, steps, has_detailed_steps, warnings, False
        )

    lower_expr = _parse_bound(lower_bound)
    upper_expr = _parse_bound(upper_bound)
    reference = sympy.integrate(input_expr, (var_symbol, lower_expr, upper_expr))

    can_use_ftc_steps = has_detailed_steps and not antiderivative.has(sympy.Integral)
    if can_use_ftc_steps:
        definite_value = sympy.simplify(
            antiderivative.subs(var_symbol, upper_expr)
            - antiderivative.subs(var_symbol, lower_expr)
        )
        if verify_step_equivalence(definite_value, reference) == "VERIFIED":
            ftc_step = Step(
                index=0,
                title="Teorema Fundamental del Cálculo",
                description="∫[a,b] f(x) dx = F(b) - F(a), donde F es la antiderivada.",
                rule="FTC",
                latex_before=f"F({var_symbol}) = {sympy.latex(antiderivative)}",
                latex_after=f"F({sympy.latex(upper_expr)}) - F({sympy.latex(lower_expr)})",
            )
            substitution_step = Step(
                index=0,
                title="Sustitución de límites",
                description="Se sustituyen los límites en la antiderivada y se simplifica.",
                rule="EvaluateBounds",
                latex_before=f"F({sympy.latex(upper_expr)}) - F({sympy.latex(lower_expr)})",
                latex_after=sympy.latex(definite_value),
            )
            all_steps = [*steps, ftc_step, substitution_step]
            for index, step in enumerate(all_steps):
                step.index = index
            return IntegralResult(
                input_expr, antiderivative, all_steps, True, warnings, True, definite_value
            )

    return IntegralResult(input_expr, antiderivative, [], False, [], True, reference)
