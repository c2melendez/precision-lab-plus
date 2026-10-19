"""
app/services/solve_service.py — `/solve` (spec, sección 8.5, `SolveRequest`).

IMPORTANTE (spec, Módulo 6): los pasos de aislamiento de variable se
verifican con `verify_equation_step_equivalence` (conjuntos solución),
NUNCA con `verify_step_equivalence` (escalar) — una ecuación completa no es
una expresión donde "antes - después == 0" tenga sentido; lo que se
preserva al transformar una ecuación es su CONJUNTO SOLUCIÓN, no un valor
escalar.

Igual que en `derivative_engine/engine.py` e `integral_service.py`: la
verificación se hace UNA vez, de forma holística, sobre el resultado final
ensamblado (la ecuación normalizada vs. una ecuación sintética construida a
partir de la(s) solución(es) propuesta(s)) — misma simplificación DEDUCIBLE
documentada en los cierres de los Módulos 4 y 5, aplicada aquí por
consistencia de diseño.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple

import sympy
from sympy import cos, cot, csc, sec, sin, tan

from app.schemas.responses import EquationSolution, ResultType, Step
from app.services import parsing
from app.services.step_verification import verify_equation_step_equivalence

_DIRECT_TRIG_FUNCTIONS = (sin, cos, tan, sec, csc, cot)


class AmbiguousVariableError(ValueError):
    """Más de un símbolo libre sin `variable` especificada -> `ErrorCode.AMBIGUOUS_VARIABLE`."""


@dataclass
class SolveResult:
    input_eq: sympy.Eq
    variable: Optional[sympy.Symbol]
    result_type: ResultType
    solutions: List[EquationSolution]
    steps: List[Step]
    has_detailed_steps: bool
    warnings: List[str]


def _equation_has_direct_trig_of_variable(eq: sympy.Eq, var: sympy.Symbol) -> bool:
    for node in sympy.preorder_traversal(eq):
        if isinstance(node, _DIRECT_TRIG_FUNCTIONS) and node.args and node.args[0] == var:
            return True
    return False


def _apply_degree_conversion(
    solutions: List[sympy.Expr], has_direct_trig: bool
) -> List[sympy.Expr]:
    """Sección 3: conversión FINAL de las soluciones (radianes -> grados),
    acotada a ecuaciones con funciones trig directas de la variable — no a
    cualquier ecuación con angle_unit='deg'."""
    if not has_direct_trig:
        return solutions
    converted = []
    for solution in solutions:
        try:
            converted.append(sympy.simplify(solution * 180 / sympy.pi))
        except Exception:
            converted.append(solution)
    return converted


def _to_equation_solution(value: sympy.Expr) -> EquationSolution:
    is_complex = value.has(sympy.I) or (value.is_number and value.is_real is False)
    return EquationSolution(text=str(value), latex=sympy.latex(value), is_complex=bool(is_complex))


def _absolute_value_equidistance_steps(
    eq: sympy.Eq, var: sympy.Symbol
) -> Optional[Tuple[List[Step], List[sympy.Expr]]]:
    """Solve |x-a|=|x-b| on R with the distinct/equal-center cases."""
    try:
        if not isinstance(eq.lhs, sympy.Abs) or not isinstance(eq.rhs, sympy.Abs):
            return None
        left_arg, right_arg = eq.lhs.args[0], eq.rhs.args[0]
        if var not in left_arg.free_symbols or var not in right_arg.free_symbols:
            return None
        if sympy.simplify(sympy.diff(left_arg, var) - 1) != 0:
            return None
        if sympy.simplify(sympy.diff(right_arg, var) - 1) != 0:
            return None
        left_center = sympy.simplify(var - left_arg)
        right_center = sympy.simplify(var - right_arg)
        if var in left_center.free_symbols or var in right_center.free_symbols:
            return None
        difference = sympy.simplify(left_center - right_center)
        midpoint = sympy.simplify((left_center + right_center) / 2)
        if difference == 0:
            description = "Como a = b, ambos valores absolutos son idénticos; toda x real es solución."
        elif difference.is_zero is False:
            description = "Como a ≠ b, la única solución real es el punto medio x = (a+b)/2."
        else:
            description = (
                "Si a ≠ b, la única solución real es x = (a+b)/2; "
                "si a = b, toda x real es solución. La raíz mostrada es condicional a a ≠ b."
            )
        step = Step(
            index=0,
            title="Equidistancia en la recta real",
            description=description,
            rule="AbsoluteValueEquidistance",
            latex_before=sympy.latex(eq),
            latex_after=sympy.latex(sympy.Eq(var, midpoint)),
        )
        return [step], [midpoint]
    except Exception:
        return None


def _absolute_value_steps(
    eq: sympy.Eq, var: sympy.Symbol
) -> Optional[Tuple[List[Step], List[sympy.Expr]]]:
    """Solve the certified real-domain absolute-value form locally, without
    changing global assumptions on symbols used by other solver paths."""
    try:
        if isinstance(eq.lhs, sympy.Abs):
            absolute, radius = eq.lhs, eq.rhs
        elif isinstance(eq.rhs, sympy.Abs):
            absolute, radius = eq.rhs, eq.lhs
        else:
            return None

        argument = absolute.args[0]
        if var not in argument.free_symbols or var in radius.free_symbols:
            return None
        if sympy.simplify(sympy.diff(argument, var) - 1) != 0:
            return None
        center = sympy.simplify(var - argument)
        if var in center.free_symbols:
            return None

        radius = sympy.simplify(radius)
        if radius.is_real is False:
            return None
        if radius.is_number and radius.is_real is True:
            if radius < 0:
                return [
                    Step(
                        index=0,
                        title="Dominio del valor absoluto",
                        description="El valor absoluto siempre es no negativo; como b < 0, no existe solución real.",
                        rule="AbsoluteValueDomain",
                        latex_before=sympy.latex(eq),
                        latex_after=r"\varnothing",
                    )
                ], []
            if radius == 0:
                solutions = [center]
                description = "Si b = 0, |x-a| solo vale cero en x = a."
            else:
                solutions = [
                    sympy.simplify(center + radius),
                    sympy.simplify(center - radius),
                ]
                description = "Si b > 0, las dos ramas x = a + b y x = a - b dan las dos raíces reales."
        else:
            solutions = [
                sympy.simplify(center + radius),
                sympy.simplify(center - radius),
            ]
            description = (
                "Para |x-a| = b: si b < 0 no hay solución; si b = 0, x = a; "
                "si b > 0, x = a ± b. Las dos expresiones son condicionales a b > 0."
            )

        latex_solutions = r",\quad ".join(
            sympy.latex(sympy.Eq(var, solution)) for solution in solutions
        )
        steps = [
            Step(
                index=0,
                title="Dominio del valor absoluto",
                description=description,
                rule="AbsoluteValueDomain",
                latex_before=sympy.latex(eq),
                latex_after=latex_solutions,
            )
        ]
        return steps, solutions
    except Exception:
        return None


def _linear_steps(eq: sympy.Eq, var: sympy.Symbol) -> Optional[Tuple[List[Step], List[sympy.Expr]]]:
    try:
        normalized = sympy.Eq(sympy.expand(eq.lhs - eq.rhs), 0)
        poly = sympy.Poly(normalized.lhs, var)
        if poly.degree() != 1:
            return None
        a, b = poly.all_coeffs()
        solution = sympy.simplify(-b / a)
        final_eq = sympy.Eq(var, solution)

        if verify_equation_step_equivalence(normalized, final_eq, var) != "VERIFIED":
            return None

        steps = [
            Step(
                index=0,
                title="Normalización",
                description="Se agrupan todos los términos en un lado de la ecuación.",
                rule="Normalize",
                latex_before=sympy.latex(eq),
                latex_after=sympy.latex(normalized),
            ),
            Step(
                index=0,
                title="Despejar la variable",
                description=f"{sympy.latex(var)} = -({sympy.latex(b)})/({sympy.latex(a)}).",
                rule="IsolateVariable",
                latex_before=sympy.latex(normalized),
                latex_after=sympy.latex(final_eq),
            ),
        ]
        return steps, [solution]
    except Exception:
        return None


def _quadratic_steps(
    eq: sympy.Eq, var: sympy.Symbol
) -> Optional[Tuple[List[Step], List[sympy.Expr]]]:
    try:
        normalized = sympy.Eq(sympy.expand(eq.lhs - eq.rhs), 0)
        poly = sympy.Poly(normalized.lhs, var)
        if poly.degree() != 2:
            return None
        a, b, c = poly.all_coeffs()
        discriminant = sympy.simplify(b**2 - 4 * a * c)
        sqrt_discriminant = sympy.sqrt(discriminant)
        solution_1 = sympy.simplify((-b + sqrt_discriminant) / (2 * a))
        solution_2 = sympy.simplify((-b - sqrt_discriminant) / (2 * a))

        final_eq = sympy.Eq(sympy.expand(a * (var - solution_1) * (var - solution_2)), 0)
        if verify_equation_step_equivalence(normalized, final_eq, var) != "VERIFIED":
            return None

        steps = [
            Step(
                index=0,
                title="Normalización",
                description="Se agrupan todos los términos en un lado de la ecuación.",
                rule="Normalize",
                latex_before=sympy.latex(eq),
                latex_after=sympy.latex(normalized),
            ),
            Step(
                index=0,
                title="Identificar coeficientes",
                description=(f"a = {sympy.latex(a)}, b = {sympy.latex(b)}, c = {sympy.latex(c)}."),
                rule="IdentifyCoefficients",
                latex_before=sympy.latex(normalized),
                latex_after=f"a={sympy.latex(a)},\\ b={sympy.latex(b)},\\ c={sympy.latex(c)}",
            ),
            Step(
                index=0,
                title="Calcular el discriminante",
                description="D = b² - 4ac.",
                rule="Discriminant",
                latex_before="b^2-4ac",
                latex_after=sympy.latex(discriminant),
            ),
            Step(
                index=0,
                title="Fórmula general",
                description="x = (-b ± √D) / (2a).",
                rule="QuadraticFormula",
                latex_before=sympy.latex(normalized),
                latex_after=(
                    f"{sympy.latex(var)}_1={sympy.latex(solution_1)},\\ "
                    f"{sympy.latex(var)}_2={sympy.latex(solution_2)}"
                ),
            ),
        ]
        solutions = [solution_1] if solution_1 == solution_2 else [solution_1, solution_2]
        return steps, solutions
    except Exception:
        return None


def solve_equation(
    equation_text: str, variable_name: Optional[str], angle_unit: str = "rad"
) -> SolveResult:
    convention_warnings = (["Sin signo =: en Resolver se interpreta la expresión como una ecuación igual a 0."]
                           if "=" not in parsing.normalize_unicode(equation_text) else [])
    eq = parsing.parse_expression_tree(equation_text, allow_equation=True)
    free_symbols = sorted(eq.free_symbols, key=lambda s: s.name)

    if not free_symbols:
        if eq is sympy.true:
            result_type = ResultType.IDENTITY
        elif eq is sympy.false:
            result_type = ResultType.CONTRADICTION
        else:
            # eq sigue siendo un sympy.Eq real (SymPy no pudo decidir la
            # verdad de inmediato, ej. Eq(sin(1), sin(1)) en algunas
            # versiones) — se compara la diferencia como antes.
            is_identity = sympy.simplify(eq.lhs - eq.rhs) == 0
            result_type = ResultType.IDENTITY if is_identity else ResultType.CONTRADICTION
        return SolveResult(eq, None, result_type, [], [], False, convention_warnings)

    # IN625 E3d2 / Algebra114 AS-PAR-01: classify the simplified
    # equation difference before solving. This catches identities such as
    # 0*x=0 and contradictions such as 0*x=5, where the original unevaluated
    # equation can still syntactically contain x after a coefficient is zero.
    difference = sympy.simplify(eq.lhs - eq.rhs)
    if difference == 0:
        return SolveResult(eq, None, ResultType.IDENTITY, [], [], False, convention_warnings)
    if not difference.free_symbols:
        return SolveResult(eq, None, ResultType.CONTRADICTION, [], [], False, convention_warnings)

    warnings: List[str] = list(convention_warnings)
    if variable_name:
        candidates = parsing.extract_candidate_identifiers(variable_name)
        if candidates != [variable_name]:
            raise parsing.ParseSecurityError(f"Nombre de variable inválido: '{variable_name}'.")
        var = sympy.Symbol(variable_name)
    else:
        if len(free_symbols) > 1:
            raise AmbiguousVariableError(
                "La ecuación tiene más de una variable libre; especifica cuál despejar "
                f"({', '.join(str(s) for s in free_symbols)})."
            )
        var = free_symbols[0]
        warnings.append(f"Variable inferida automáticamente: '{var}'.")

    parameters = [str(symbol) for symbol in free_symbols if symbol != var]
    if var in free_symbols and parameters:
        warnings.append(f"Se despeja {var}; parámetros libres: {', '.join(parameters)}.")

    has_direct_trig = _equation_has_direct_trig_of_variable(eq, var)

    steps_and_solutions = _absolute_value_equidistance_steps(eq, var)
    if steps_and_solutions is None:
        steps_and_solutions = _absolute_value_steps(eq, var)
    if steps_and_solutions is None:
        steps_and_solutions = _linear_steps(eq, var)
    if steps_and_solutions is None:
        steps_and_solutions = _quadratic_steps(eq, var)

    if steps_and_solutions is not None:
        steps, solutions = steps_and_solutions
        has_detailed_steps = True
    else:
        raw_solutions = sympy.solve(eq, var)
        solutions = list(raw_solutions) if isinstance(raw_solutions, (list, tuple)) else []
        steps = []
        has_detailed_steps = False

    if angle_unit == "deg":
        solutions = _apply_degree_conversion(solutions, has_direct_trig)

    for index, step in enumerate(steps):
        step.index = index

    equation_solutions = [_to_equation_solution(solution) for solution in solutions]

    return SolveResult(
        eq,
        var,
        ResultType.EQUATION_SOLUTIONS,
        equation_solutions,
        steps,
        has_detailed_steps,
        warnings,
    )
