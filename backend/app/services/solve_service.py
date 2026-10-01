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

from app.schemas.responses import ComplexGraphPoint, EquationSolution, ResultType, Step
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
    graph_points: Optional[List[ComplexGraphPoint]] = None


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


def _bounded_trig_polynomial_solutions(
    expr: sympy.Expr, var: sympy.Symbol, interval: sympy.Interval
) -> Optional[List[sympy.Expr]]:
    """Solve each algebraic branch of a polynomial in one trig function.

    The generic bounded solver may leave periodic intersections unevaluated;
    filtering its principal solve() roots can silently lose valid branches.
    Return None unless every branch has a finite, resolved solution set.
    """
    atoms = expr.atoms(sympy.sin, sympy.cos, sympy.tan)
    if len(atoms) != 1:
        return None
    atom = next(iter(atoms))
    if atom.args != (var,):
        return None
    u = sympy.Dummy("trig_value", real=True)
    transformed = expr.xreplace({atom: u})
    if transformed.free_symbols - {u}:
        return None
    try:
        polynomial = sympy.Poly(transformed, u)
    except sympy.PolynomialError:
        return None
    if not 2 <= polynomial.degree() <= 4:
        return None
    roots = sympy.solveset(polynomial.as_expr(), u, domain=sympy.S.Reals)
    if not isinstance(roots, sympy.FiniteSet):
        return None
    solutions = sympy.EmptySet
    for value in roots:
        branch = sympy.solveset(atom - value, var, domain=interval)
        if branch is sympy.EmptySet:
            continue
        if not isinstance(branch, sympy.FiniteSet):
            return None
        solutions = solutions.union(branch)
    return sorted(list(solutions), key=sympy.default_sort_key)


def _real_affine_atan_sum(eq: sympy.Eq, var: sympy.Symbol):
    """Reduce a two-atan sum in the principal tangent range, with a branch guard."""
    for total, target in ((eq.lhs, eq.rhs), (eq.rhs, eq.lhs)):
        if not isinstance(total, sympy.Add) or len(total.args) != 2:
            continue
        if any(getattr(term, "func", None) != sympy.atan for term in total.args):
            continue
        target = sympy.simplify(target)
        if target.free_symbols or target.is_real is not True:
            continue
        if (target > -sympy.pi/2) is not sympy.true or (target < sympy.pi/2) is not sympy.true:
            continue
        u, v = (term.args[0] for term in total.args)
        try:
            polynomials = [sympy.Poly(argument, var) for argument in (u, v)]
        except sympy.PolynomialError:
            continue
        if any(poly.degree() > 1 or any(c.is_real is not True or c.free_symbols for c in poly.all_coeffs())
               for poly in polynomials):
            continue
        sine, cosine = sympy.simplify(sympy.sin(target)), sympy.simplify(sympy.cos(target))
        if sine.is_algebraic is not True or cosine.is_algebraic is not True:
            continue
        denominator = 1-u*v
        # cos(atan(u)+atan(v)) has the sign of 1-u*v. Requiring it
        # positive fixes the sum in (-pi/2,pi/2), where tan is injective.
        # Multiplying across the tangent identity alone would retain the
        # root belonging to a different branch of the original equation.
        reduced = sympy.expand(cosine*(u+v)-sine*denominator)
        return sympy.Eq(reduced, 0, evaluate=False), denominator
    return None


def solve_equation(
    equation_text: str,
    variable_name: Optional[str],
    angle_unit: str = "rad",
    domain: str = "complex",
    domain_lower: Optional[str] = None,
    domain_upper: Optional[str] = None,
    domain_lower_inclusive: bool = True,
    domain_upper_inclusive: bool = True,
) -> SolveResult:
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
        return SolveResult(eq, None, result_type, [], [], False, [])

    warnings: List[str] = []
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

    original_inverse_eq = None
    if domain == "real":
        # Calculator convention for real arccot: range (0, pi), expressed
        # as pi/2 - atan(x). SymPy's principal acot branch differs for
        # negative reals and would incorrectly report no solution for
        # cases such as acot(x)=2*pi/3.
        eq = eq.replace(
            lambda node: getattr(node, "func", None) == sympy.acot,
            lambda node: sympy.pi / 2 - sympy.atan(node.args[0]),
        )

        # asin(u) + acos(u) = pi/2 on the real principal branches. SymPy
        # 1.13 raises NotImplementedError for asin(x)=acos(x) because it
        # treats the two inverse functions as independent generators.
        # Reduce this exact same-argument identity before the generic
        # solver so the usual domain/solution pipeline remains in charge.
        if isinstance(eq, sympy.Equality):
            lhs, rhs = eq.lhs, eq.rhs
            if (
                getattr(lhs, "func", None) == sympy.asin
                and getattr(rhs, "func", None) == sympy.acos
                and lhs.args == rhs.args
            ):
                eq = sympy.Eq(lhs, sympy.pi / 4)
            elif (
                getattr(lhs, "func", None) == sympy.acos
                and getattr(rhs, "func", None) == sympy.asin
                and lhs.args == rhs.args
            ):
                eq = sympy.Eq(rhs, sympy.pi / 4)

            # Same-argument real principal inverse hyperbolic identities.
            # atanh(u)-asinh(u) is odd and strictly increasing on (-1,1):
            # its derivative is 1/(1-u**2)-1/sqrt(1+u**2)>0 except at 0.
            # Thus equality holds only at u=0. For u>=1, asinh(u)>acosh(u)
            # since sqrt(u**2+1)>sqrt(u**2-1) in their logarithmic forms.
            # Only reduce identical arguments; other comparisons continue
            # through the generic solver, as do complex-domain requests.
            functions = {getattr(lhs, "func", None), getattr(rhs, "func", None)}
            if lhs.args == rhs.args and functions == {sympy.atanh, sympy.asinh}:
                original_inverse_eq = eq
                eq = sympy.Eq(lhs.args[0], 0, evaluate=False)
            elif lhs.args == rhs.args and functions == {sympy.acosh, sympy.asinh}:
                original_inverse_eq = eq
                eq = sympy.Eq(1, 0, evaluate=False)

    atan_denominator = None
    atan_reduction = _real_affine_atan_sum(eq, var) if domain == "real" else None
    if atan_reduction is not None:
        original_inverse_eq = eq
        eq, atan_denominator = atan_reduction

    has_direct_trig = _equation_has_direct_trig_of_variable(eq, var)

    bounded_real_domain = (
        domain == "real" and domain_lower is not None and domain_upper is not None
    )

    if bounded_real_domain:
        lower_expr = parsing.parse_expression_tree(domain_lower, allow_equation=False)
        upper_expr = parsing.parse_expression_tree(domain_upper, allow_equation=False)
        if lower_expr.free_symbols or upper_expr.free_symbols:
            raise parsing.ParseSecurityError("Los límites del dominio deben ser valores concretos.")
        interval = sympy.Interval(
            lower_expr,
            upper_expr,
            left_open=not domain_lower_inclusive,
            right_open=not domain_upper_inclusive,
        )
        trig_solutions = _bounded_trig_polynomial_solutions(eq.lhs - eq.rhs, var, interval)
        solution_set = sympy.solveset(eq, var, domain=interval) if trig_solutions is None else None
        if trig_solutions is not None:
            solutions = trig_solutions
        elif isinstance(solution_set, sympy.FiniteSet):
            solutions = sorted(list(solution_set), key=sympy.default_sort_key)
        else:
            raw_solutions = sympy.solve(eq, var)
            candidates = list(raw_solutions) if isinstance(raw_solutions, (list, tuple)) else []
            solutions = [s for s in candidates if interval.contains(s) is sympy.true]
        steps = []
        has_detailed_steps = False
    else:
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

    if atan_denominator is not None:
        branch_solutions = []
        for solution in solutions:
            if solution.is_real is False:
                continue
            branch_value = sympy.simplify(atan_denominator.subs(var, solution))
            if branch_value.is_positive is None:
                raise NotImplementedError("No se pudo verificar la rama principal de la suma de arctangentes.")
            if branch_value.is_positive:
                branch_solutions.append(solution)
        solutions = branch_solutions

    if angle_unit == "deg":
        solutions = _apply_degree_conversion(solutions, has_direct_trig)

    if original_inverse_eq is not None:
        # Retain the user's equation. Algebraic steps for the reduced
        # condition alone would omit the real-branch identity above.
        eq = original_inverse_eq
        steps = []
        has_detailed_steps = False

    if domain == "real":
        real_solutions: List[sympy.Expr] = []
        for solution in solutions:
            real_flag = solution.is_real
            if real_flag is True:
                real_solutions.append(solution)
                continue
            if real_flag is False or solution.has(sympy.I):
                continue
            # For exact numeric expressions whose assumptions are
            # inconclusive, inspect a numerical approximation before
            # deciding. Symbolic unknowns are preserved rather than
            # discarded speculatively.
            if solution.free_symbols:
                real_solutions.append(solution)
                continue
            try:
                numeric = complex(sympy.N(solution))
            except (TypeError, ValueError, OverflowError):
                real_solutions.append(solution)
                continue
            if abs(numeric.imag) < 1e-12:
                real_solutions.append(sympy.simplify(sympy.re(solution)))
        solutions = real_solutions

    for index, step in enumerate(steps):
        step.index = index

    equation_solutions = [_to_equation_solution(solution) for solution in solutions]
    graph_points = None
    if solutions and len(solutions) <= 20 and any(value.has(sympy.I) for value in solutions):
        points = []
        for value in solutions:
            if value.free_symbols or value.is_number is not True:
                break
            try:
                re_value = float(sympy.N(sympy.re(value)))
                im_value = float(sympy.N(sympy.im(value)))
            except (AttributeError, TypeError, ValueError, OverflowError):
                break
            if not all(sympy.Float(v).is_finite and abs(v) <= 1e6 for v in (re_value, im_value)):
                break
            points.append(ComplexGraphPoint(re=re_value, im=im_value, label=str(value)))
        if len(points) == len(solutions):
            graph_points = points

    return SolveResult(
        eq,
        var,
        ResultType.EQUATION_SOLUTIONS,
        equation_solutions,
        steps,
        has_detailed_steps,
        warnings,
        graph_points,
    )
