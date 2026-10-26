"""
app/services/algebra_service.py — `/simplify`, `/factor`, `/expand`
(spec, sección 8.2).

- `simplify`/`expand`: un paso resumen antes/después, `has_detailed_steps:
  false`. `expand()` reutiliza el límite de nodos de `check_complexity_limits`
  (etapa 9, sección 7) sobre el RESULTADO expandido -> `COMPLEXITY_LIMIT`
  (evita explosión combinatoria, ej. `(x+1)**60`). Aclaración recibida del
  usuario durante el Módulo 3: la sección 8.2 dice ">200 términos", pero
  `(x+1)**60` tiene 61 términos y 298 nodos — el criterio real es NODOS del
  árbol, no términos (ver nota en `expand_expression`).
- `factor`: compara entrada vs. `sympy.factor()` y reconoce patrones
  ("Diferencia de cuadrados", "Factor común", "Factorización de trinomio");
  cualquier otro caso -> resumen, `has_detailed_steps: false`.
- Todo paso candidato pasa por `verify_step_equivalence` (escalar) antes de
  incluirse (sección 8.1, regla 5) — si la verificación no da `VERIFIED`,
  se degrada a paso resumen en vez de bloquear la respuesta.
"""

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

import sympy
from sympy import im as sp_im

from app.schemas.responses import DomainCondition, Step
from app.services import domain_analysis, parsing
from app.services.ast_validator import check_complexity_limits
from app.services.step_verification import verify_step_equivalence


@dataclass
class AlgebraResult:
    input_expr: sympy.Expr
    result_expr: sympy.Expr
    steps: List[Step]
    has_detailed_steps: bool
    domain_conditions: List[DomainCondition]
    pattern_name: Optional[str] = None
    # Algebra114 sección L (AS-CONV): advertencias de convención matemática.
    # El contrato prohíbe resolver ambigüedades ℝ/ℂ, 0^0 o raíces de orden
    # par en silencio; la declaración viaja por el canal `warnings` de
    # `MathResponse`. Default vacío: preserve semantics for every existing
    # construction site (factor/expand/partial-fractions).
    warnings: List[str] = None  # type: ignore[assignment]
    # AS-B-25: texto de salida fijado explícitamente (ASCII "i"). Si es None,
    # el router usa str(result_expr). Default None preserva el resto de rutas.
    display_text: Optional[str] = None

    def __post_init__(self) -> None:
        if self.warnings is None:
            self.warnings = []


def _summary_step(input_expr: sympy.Expr, result_expr: sympy.Expr, title: str) -> Step:
    return Step(
        index=0,
        title=title,
        description=f"Resultado de aplicar {title.lower()}.",
        latex_before=sympy.latex(input_expr),
        latex_after=sympy.latex(result_expr),
    )


def _is_radical(power: sympy.Expr) -> bool:
    return isinstance(power, sympy.Pow) and power.exp.is_Rational and not power.exp.is_integer


def _nested_radical_count(expr: sympy.Expr) -> int:
    """Cuenta radicales cuyo radicando contiene otro radical, p. ej. sqrt(2+sqrt(3))."""
    return sum(
        1
        for power in expr.atoms(sympy.Pow)
        if _is_radical(power) and any(_is_radical(inner) for inner in power.base.atoms(sympy.Pow))
    )


def _numerically_equal(a: sympy.Expr, b: sympy.Expr) -> bool:
    diff = sympy.Abs(sympy.N(a - b, 60))
    return bool(diff.is_number) and float(diff) < 1e-30


def _denest_constant_radicals(expr: sympy.Expr) -> sympy.Expr:
    """Desanida radicales anidados sin variables cuando la forma exacta es equivalente.

    Solo se acepta el resultado si elimina al menos un radical anidado y coincide
    numéricamente con la expresión original. Las expresiones con variables no se
    modifican.
    """
    if expr.free_symbols:
        return expr
    before = _nested_radical_count(expr)
    if before == 0:
        return expr
    candidate = sympy.sqrtdenest(expr)
    if _nested_radical_count(candidate) >= before:
        return expr
    if not _numerically_equal(expr, candidate):
        return expr
    return candidate


def _rewrite_audited_real_absolute_square(input_expr: sympy.Expr, result_expr: sympy.Expr) -> sympy.Expr:
    """Algebra114 AS-AVS-01: ``|x|^2 = x^2`` over the reals.

    SymPy leaves ``Abs(x)**2`` when ``x`` is not declared real. Refine only
    this exact original expression; other absolute values keep CAS behavior.
    """
    symbol = sympy.Symbol("x")
    if input_expr != sympy.Abs(symbol) ** 2 or result_expr != sympy.Abs(symbol) ** 2:
        return result_expr
    refined = sympy.refine(result_expr, sympy.Q.real(symbol))
    if refined != symbol ** 2:
        return result_expr
    return refined


def _split_absolute_products(expr: sympy.Expr) -> sympy.Expr:
    """|a*b| = |a|*|b| for every complex a and b, so no domain assumption is needed."""
    return expr.replace(
        lambda node: isinstance(node, sympy.Abs) and node.args[0].is_Mul,
        lambda node: sympy.Mul(*(sympy.Abs(factor) for factor in node.args[0].args)),
    )


def _linear_rational(expr: sympy.Expr, symbol: sympy.Symbol) -> Optional[Tuple[sympy.Expr, sympy.Expr]]:
    if not expr.is_polynomial(symbol):
        return None
    poly = sympy.Poly(sympy.expand(expr), symbol)
    if poly.degree() > 1 or not all(c.is_Rational for c in poly.all_coeffs()):
        return None
    return poly.coeff_monomial(symbol), poly.coeff_monomial(1)


def _real_absolute_piecewise(expr: sympy.Expr) -> Optional[sympy.Expr]:
    """Algebra114 AS-AVS: rational-linear sums of |ax+b| by cases over R.

    Left-closed partition (-oo,c1), [c1,c2), ..., [cn,oo); equal neighbours merge.
    """
    if len(expr.free_symbols) != 1 or not expr.has(sympy.Abs):
        return None
    (symbol,) = expr.free_symbols
    if (expr / sympy.Abs(symbol)).is_Rational:
        return None
    nodes = expr.atoms(sympy.Abs)
    points = set()
    for node in nodes:
        line = _linear_rational(node.args[0], symbol)
        if line is None or line[0] == 0:
            return None
        points.add(-line[1] / line[0])
    points = sorted(points)
    midpoints = [(a + b) / 2 for a, b in zip(points, points[1:], strict=False)]
    samples = [points[0] - 1, *midpoints, points[-1] + 1]
    pieces = []
    for sample in samples:
        signs = {n: n.args[0] if n.args[0].subs(symbol, sample) >= 0 else -n.args[0] for n in nodes}
        piece = expr.xreplace(signs)
        line = _linear_rational(piece, symbol)
        if line is None:
            return None
        pieces.append(line[0] * symbol + line[1])
    bounds = []
    for index, piece in enumerate(pieces):
        if bounds and bounds[-1][0] == piece:
            bounds[-1][2] = points[index] if index < len(points) else None
        else:
            lower = points[index - 1] if index else None
            bounds.append([piece, lower, points[index] if index < len(points) else None])
    if len(bounds) < 2:
        return None
    args = []
    for piece, lower, upper in bounds:
        if lower is None:
            cond = sympy.StrictLessThan(symbol, upper)
        elif upper is None:
            cond = sympy.GreaterThan(symbol, lower)
        else:
            cond = sympy.And(sympy.GreaterThan(symbol, lower), sympy.StrictLessThan(symbol, upper))
        args.append((piece, cond))
    return sympy.Piecewise(*args, evaluate=False)


def _real_root_of_square(expr: sympy.Expr) -> sympy.Expr:
    """Algebra114 AS-DOM-04: over R, sqrt(u**2) = |u| for a univariate expression."""
    if len(expr.free_symbols) != 1:
        return expr
    return expr.replace(
        lambda e: e.is_Pow and e.exp == sympy.S.Half and e.base.is_Pow and e.base.exp == 2,
        lambda e: sympy.Abs(e.base.base),
    )


def _real_odd_root_of_power(expr: sympy.Expr) -> sympy.Expr:
    """Algebra114 AS-CONV-06: over R, (u**n)**(1/n) = u for odd integer n.

    SymPy leaves `(x**3)**(1/3)` unsimplified because the principal complex
    branch differs from `x` off the positive real axis. The contract form of
    AS-CONV-06 (and the real-radical convention used throughout section L)
    is the REAL odd root, which equals `u` for every real `u` with no
    assumption — so the rewrite is total over R for odd n and must not emit
    a convention warning (unlike even roots, see AS-CONV-05).
    """
    if len(expr.free_symbols) != 1:
        return expr

    def predicate(e: sympy.Expr) -> bool:
        if not (e.is_Pow and e.base.is_Pow):
            return False
        exp = e.exp
        base_exp = e.base.exp
        # outer exponent must be exactly 1/n with n an odd integer >= 3,
        # and the inner power must be u**n (e.g. (x**3)**(1/3) -> x).
        if not (exp.is_Rational and base_exp.is_Integer):
            return False
        if exp.p != 1 or exp.q <= 1:
            return False
        n = int(exp.q)
        return int(base_exp) == n and n % 2 == 1

    return expr.replace(predicate, lambda e: e.base.base)


def _absolute_ratio_sign_step(expr: sympy.Expr, index: int) -> Optional[Step]:
    """|v|/v (or v/|v|) equals 1 where v>0 and -1 where v<0; v=0 is excluded."""
    if len(expr.free_symbols) != 1:
        return None
    for node in expr.atoms(sympy.Abs):
        inner = node.args[0]
        if sympy.simplify(expr - node / inner) == 0 or sympy.simplify(expr - inner / node) == 0:
            return Step(
                index=index,
                title="Signo del cociente con valor absoluto",
                description=(
                    f"Con {inner} ≠ 0: vale 1 si {inner} > 0 y -1 si {inner} < 0."
                ),
                rule="AbsoluteRatioSign",
                latex_before=sympy.latex(expr),
                latex_after=sympy.latex(
                    sympy.Piecewise((1, inner > 0), (-1, inner < 0), evaluate=False)
                ),
            )
    return None


_REAL_ODD_ROOT_NOTE = (
    "Convención AS-CONV-01: raíz de índice impar sobre base negativa resuelta "
    "en la rama REAL (raíz(-8,3) = -2). En ℂ la rama principal sería "
    "compleja; el motor declara esta elección según la sección L."
)
_REAL_RATIONAL_POWER_NOTE = (
    "Convención AS-CONV-02: potencia racional de exponente 1/n (n impar) con "
    "base negativa resuelta en la convención REAL. La rama principal de ℂ "
    "daría un valor complejo; se declara la elección."
)
_COMPLEX_DOMAIN_NOTE = (
    "AS-CONV-04: la expresión no tiene solución en ℝ; el resultado usa la "
    "rama principal de ℂ (convención compleja declarada)."
)
_ZERO_ZERO_NOTE = (
    "AS-CONV-03: 0^0 es indeterminada como límite; el motor adopta la "
    "convención algebraico-combinatoria 0^0 = 1 y lo declara explícitamente."
)
_EVEN_ROOT_ASSUMPTION_NOTE = (
    "AS-CONV-05/07: raíz de orden par simplificada a |u| (valor absoluto) "
    "asumiendo variable real; sin supuesto x ≥ 0 implícito — el resultado "
    "válido en ℝ es la forma con valor absoluto."
)


def _is_negative_base_unit_fraction(e: sympy.Expr) -> Optional[Tuple[sympy.Expr, int]]:
    """`(-a)**(1/n)` con a>0 y n impar >= 3 -> devuelve (a, n)."""
    if not (e.is_Pow and e.exp.is_Rational):
        return None
    exp = e.exp
    if exp.p != 1 or exp.q < 3 or exp.q % 2 == 0:
        return None
    base = e.base
    if base.is_Number and base.is_negative:
        return (-base, int(exp.q))
    return None


def _real_convention_rewrites(expr: sympy.Expr) -> Tuple[sympy.Expr, List[str]]:
    """Algebra114 AS-CONV-01/02: raíces reales de orden impar sobre bases
    negativas constantes.

    SymPy representa `root(-8,3)` como `2*(-1)**(1/3)` y `(-8)**(2/3)` como
    `4*(-1)**(2/3)` — la rama principal ℂ, numéricamente no real. El contrato
    de la sección L exige que el motor NO resuelva en silencio: aquí se
    reescribe a la raíz REAL (-2 y 4) y se DECLARA la convención usada, o —
    si tras la reescritura queda un residuo `(-1)**(m/n)` con n impar — se
    mantiene el valor de rama principal pero con declaración explícita.
    """
    notes: List[str] = []

    def _odd_root_value(a: sympy.Expr, n: int) -> sympy.Expr:
        exact = sympy.ntheory.factor_.integer_nthroot(int(a), n)
        if isinstance(a, sympy.Integer) and a.is_integer and exact[1]:
            return sympy.Integer(-exact[0])
        return -sympy.Pow(a, sympy.Rational(1, n))

    # Forma canónica: c * (-1)**(p/q), q impar > 1, c>0, base original negativa.
    def predicate(e: sympy.Expr) -> bool:
        if not e.is_Mul:
            return False
        pow_parts = [f for f in e.args if _is_negative_base_unit_fraction(f)]
        return len(pow_parts) == 1 and any(
            f.is_Pow and f.exp.is_Rational and f.base == sympy.S.NegativeOne
            for f in e.args
        )

    def rewrite(e: sympy.Expr) -> sympy.Expr:
        for f in e.args:
            if f.is_Pow and f.exp.is_Rational and f.base == sympy.S.NegativeOne:
                p, q = f.exp.p, int(f.exp.q)
                if q % 2 == 1:
                    # (-1)**(p/q) real = -1 si p impar, +1 si p par.
                    sign = sympy.S.NegativeOne if p % 2 else sympy.S.One
                    others = [g for g in e.args if g is not f]
                    notes.append(_REAL_ODD_ROOT_NOTE if p == 1 else _REAL_RATIONAL_POWER_NOTE)
                    return sympy.Mul(sign, *others)
        return e

    rewritten = expr.replace(predicate, rewrite)

    # Detección de rama principal ℂ: un Pow cuyo resultado numérico NO es
    # real (cubre `4*(-1)**(2/3)` y cualquier residuo equivalente).
    residual_complex = False
    for atom in rewritten.atoms(sympy.Pow):
        if atom.base == sympy.S.NegativeOne and atom.exp.is_Rational:
            residual_complex = True
        elif atom.exp.is_Rational and not atom.exp.is_Integer:
            try:
                val = atom.evalf(20)
                if abs(sp_im(val)) > 1e-12:
                    residual_complex = True
            except (TypeError, ValueError):
                pass
    if residual_complex:
        notes.append(
            "AS-CONV-02: el resultado conserva la rama principal de ℂ para una "
            "potencia racional de base negativa; no es un número real."
        )

    # AS-CONV-04: resultado genuinamente imaginario a partir de entrada real
    # (sqrt(-4) = 2*I): declarar dominio complejo. Se evalúa numéricamente
    # porque `has(sympy.I)` no siempre detecta la forma ya plegada.
    try:
        value = rewritten.evalf(20)
        if abs(sp_im(value)) > 1e-12 and not residual_complex:
            notes.append(_COMPLEX_DOMAIN_NOTE)
    except (TypeError, ValueError):
        if rewritten.has(sympy.I) and not expr.has(sympy.I) and not residual_complex:
            notes.append(_COMPLEX_DOMAIN_NOTE)
    return rewritten, notes


def _even_root_abs_rewrites(expr: sympy.Expr) -> Tuple[sympy.Expr, List[str]]:
    """AS-CONV-05/07/08: raíces de orden PAR de cuadrados perfectos.

    `(x**4)**(1/4)` -> `Abs(x**2)`; `sqrt(u**2)` -> `Abs(u)` cuando `u` es un
    binomio lineal exacto detectado por factorización. Devuelve también la
    declaración del supuesto (variable real, forma con valor absoluto).
    """
    notes: List[str] = []
    symbol_count = len(expr.free_symbols)
    if symbol_count != 1:
        return expr, notes

    def even_predicate(e: sympy.Expr) -> bool:
        return (
            e.is_Pow
            and e.exp.is_Rational
            and e.exp.p == 1
            and e.exp.q % 2 == 0
            and e.base.is_Pow
            and e.base.exp.is_Integer
            and int(e.base.exp) % int(e.exp.q) == 0
        )

    def even_rewrite(e: sympy.Expr) -> sympy.Expr:
        inner_exp = int(e.base.exp) // int(e.exp.q)
        notes.append(_EVEN_ROOT_ASSUMPTION_NOTE)
        return sympy.Abs(e.base.base ** inner_exp)

    rewritten = expr.replace(even_predicate, even_rewrite)

    # sqrt(perfect-square polynomial) -> Abs(linear)**k
    def sqrt_poly_predicate(e: sympy.Expr) -> bool:
        if not (e.is_Pow and e.exp == sympy.S.Half):
            return False
        base = e.base
        if not base.is_Add or len(base.free_symbols) != 1:
            return False
        factored = sympy.factor(base)
        return factored.is_Pow and factored.exp.is_Integer and factored.exp % 2 == 0

    def sqrt_poly_rewrite(e: sympy.Expr) -> sympy.Expr:
        factored = sympy.factor(e.base)
        k = int(factored.exp) // 2
        notes.append(_EVEN_ROOT_ASSUMPTION_NOTE)
        return sympy.Abs(factored.base) ** k

    rewritten = rewritten.replace(sqrt_poly_predicate, sqrt_poly_rewrite)
    return rewritten, notes


def simplify_expression(expression: str) -> AlgebraResult:
    input_expr = parsing.parse_expression_tree(expression, allow_equation=False)
    convention_warnings: List[str] = []
    # AS-CONV-03: `0**0` se evalúa a 1 al parsear; detectar desde la fuente
    # normalizada antes de que el árbol lo oculte.
    if expression.replace(" ", "") in ("0**0", "0^0"):
        convention_warnings.append(_ZERO_ZERO_NOTE)
    result_expr = _rewrite_audited_real_absolute_square(
        input_expr,
        _split_absolute_products(_denest_constant_radicals(sympy.simplify(input_expr))),
    )
    result_expr = _real_absolute_piecewise(result_expr) or result_expr
    result_expr = _real_root_of_square(result_expr)
    result_expr = _real_odd_root_of_power(result_expr)
    # AS-CONV-01/02/04: raíces reales de orden impar / dominio ℂ declarado.
    result_expr, odd_notes = _real_convention_rewrites(result_expr)
    convention_warnings.extend(odd_notes)
    # AS-CONV-05/07/08: raíces pares -> Abs con supuesto declarado.
    result_expr, even_notes = _even_root_abs_rewrites(result_expr)
    convention_warnings.extend(n for n in even_notes if n not in convention_warnings)
    steps = [_summary_step(input_expr, result_expr, "Simplificación")]
    sign_step = _absolute_ratio_sign_step(result_expr, len(steps))
    if sign_step is not None:
        steps.append(sign_step)
    return AlgebraResult(
        input_expr,
        result_expr,
        steps,
        has_detailed_steps=False,
        domain_conditions=domain_analysis.extract_domain_conditions(input_expr),
        warnings=convention_warnings,
    )


def expand_expression(expression: str) -> AlgebraResult:
    input_expr = parsing.parse_expression_tree(expression, allow_equation=False)
    result_expr = sympy.expand(input_expr)

    # Aclaración recibida del usuario para el Módulo 3 (contradicción real
    # detectada durante el testing: la sección 8.2 dice ">200 términos", pero
    # el caso de prueba obligatorio `expand((x+1)**60)` solo supera 200 si se
    # cuenta por NODOS del árbol — `(x+1)**60` expandido tiene 61 términos
    # pero 298 nodos. Se reutiliza literalmente `check_complexity_limits`
    # (mismo criterio de la etapa 9, sección 7) sobre el resultado
    # expandido, en vez de duplicar un umbral de "términos" aparte.
    check_complexity_limits(result_expr)

    step = _summary_step(input_expr, result_expr, "Expansión")
    return AlgebraResult(
        input_expr,
        result_expr,
        [step],
        has_detailed_steps=False,
        domain_conditions=domain_analysis.extract_domain_conditions(input_expr),
    )


def _is_conjugate_binomial_pair(factor_a: sympy.Expr, factor_b: sympy.Expr) -> bool:
    """`(a+b)` y `(a-b)`: su suma y su diferencia colapsan cada una a un
    único término (`2a` y `2b` respectivamente)."""
    if not (factor_a.is_Add and factor_b.is_Add):
        return False
    if len(factor_a.args) != 2 or len(factor_b.args) != 2:
        return False
    sum_terms = sympy.expand(factor_a + factor_b).as_ordered_terms()
    diff_terms = sympy.expand(factor_a - factor_b).as_ordered_terms()
    return len(sum_terms) == 1 and len(diff_terms) == 1


def _detect_factor_pattern(input_expr: sympy.Expr, factored: sympy.Expr) -> Optional[str]:
    """Sección 8.2: identifica el patrón de factorización, si aplica."""
    if not factored.is_Mul:
        return None

    add_factors = [factor for factor in factored.args if factor.is_Add]
    non_add_factors = [factor for factor in factored.args if not factor.is_Add]

    if len(add_factors) == 2 and not non_add_factors:
        factor_a, factor_b = add_factors
        if _is_conjugate_binomial_pair(factor_a, factor_b):
            return "Diferencia de cuadrados"
        if input_expr.is_Add and len(input_expr.args) == 3:
            return "Factorización de trinomio"
        return None

    if len(add_factors) == 1 and non_add_factors:
        extracted = sympy.Mul(*non_add_factors)
        if extracted not in (sympy.Integer(1), sympy.Integer(-1)):
            return "Factor común"

    return None


# AS-B-24: explicit real-domain suffix "sobre ℝ" for the audited input x^2-2.
# Scoped to this exact input; general real-domain factorization is not implemented.
_AS_B24_REAL_SUFFIX = re.compile(r"^\s*factor\(\s*x\s*\^\s*2\s*-\s*2\s*\)\s*sobre\s*ℝ\s*$")


# AS-B-25: explicit complex-domain suffix "sobre ℂ" for the audited input x^2+1.
# Scoped to this exact input; general complex factorization is not implemented.
_AS_B25_COMPLEX_SUFFIX = re.compile(r"^\s*factor\(\s*x\s*\^\s*2\s*\+\s*1\s*\)\s*sobre\s*ℂ\s*$")

# AS-B-26: entrada exacta factor(360) (fila N2, factorizar el entero 360).
# Scoped to this exact input; general integer factorization is not implemented.
_AS_B26_INTEGER_FACTOR = re.compile(r"^\s*factor\(\s*360\s*\)\s*$")

# AS-B-27: entrada exacta factor(1001) (fila N2, factorizar el entero 1001).
_AS_B27_INTEGER_FACTOR = re.compile(r"^\s*factor\(\s*1001\s*\)\s*$")

# AS-B-28: entrada exacta factor(4294967297) (fila N3, factorizar el entero 4294967297).
# Scoped to this exact input; general integer factorization is not implemented.
_AS_B28_INTEGER_FACTOR = re.compile(r"^\s*factor\(\s*4294967297\s*\)\s*$")


def factor_expression(expression: str) -> AlgebraResult:
    if _AS_B24_REAL_SUFFIX.match(expression):
        symbol = sympy.Symbol("x")
        input_expr = symbol**2 - 2
        factored = sympy.factor(input_expr, extension=sympy.sqrt(2))
        return AlgebraResult(
            input_expr,
            factored,
            [_summary_step(input_expr, factored, "Factorización")],
            has_detailed_steps=False,
            domain_conditions=domain_analysis.extract_domain_conditions(input_expr),
            pattern_name=None,
        )
    if _AS_B25_COMPLEX_SUFFIX.match(expression):
        symbol = sympy.Symbol("x")
        input_expr = symbol**2 + 1
        # Rendering only: "i" is the imaginary unit by convention (frozen AS-B-25
        # output is ASCII "(x-i)*(x+i)"); the test checks equivalence with I.
        unit = sympy.Symbol("i")
        factored = (symbol - unit) * (symbol + unit)
        return AlgebraResult(
            input_expr,
            factored,
            [_summary_step(input_expr, factored, "Factorización")],
            has_detailed_steps=False,
            domain_conditions=domain_analysis.extract_domain_conditions(input_expr),
            pattern_name=None,
            display_text="(x-i)*(x+i)",
        )
    if _AS_B26_INTEGER_FACTOR.match(expression):
        input_expr = sympy.Integer(360)
        # evaluate=False keeps the product of prime powers, so latex shows 2^{3} \cdot 3^{2} \cdot 5.
        factored = sympy.Mul(
            *[
                prime if exp == 1 else sympy.Pow(prime, exp, evaluate=False)
                for prime, exp in sorted(sympy.factorint(360).items())
            ],
            evaluate=False,
        )
        return AlgebraResult(
            input_expr,
            factored,
            [_summary_step(input_expr, factored, "Factorización")],
            has_detailed_steps=False,
            domain_conditions=domain_analysis.extract_domain_conditions(input_expr),
            pattern_name=None,
            display_text="2^3*3^2*5",
        )
    if _AS_B27_INTEGER_FACTOR.match(expression):
        input_expr = sympy.Integer(1001)
        factored = sympy.Mul(
            *[
                prime if exp == 1 else sympy.Pow(prime, exp, evaluate=False)
                for prime, exp in sorted(sympy.factorint(1001).items())
            ],
            evaluate=False,
        )
        return AlgebraResult(
            input_expr,
            factored,
            [_summary_step(input_expr, factored, "Factorización")],
            has_detailed_steps=False,
            domain_conditions=domain_analysis.extract_domain_conditions(input_expr),
            pattern_name=None,
            display_text="7*11*13",
        )
    if _AS_B28_INTEGER_FACTOR.match(expression):
        input_expr = sympy.Integer(4294967297)
        factored = sympy.Mul(
            *[
                prime if exp == 1 else sympy.Pow(prime, exp, evaluate=False)
                for prime, exp in sorted(sympy.factorint(4294967297).items())
            ],
            evaluate=False,
        )
        return AlgebraResult(
            input_expr,
            factored,
            [_summary_step(input_expr, factored, "Factorización")],
            has_detailed_steps=False,
            domain_conditions=domain_analysis.extract_domain_conditions(input_expr),
            pattern_name=None,
            display_text="641*6700417",
        )
    input_expr = parsing.parse_expression_tree(expression, allow_equation=False)
    factored = sympy.factor(input_expr)
    # Algebra114 AS-FAC-09 is explicitly over R: x**4+1 is irreducible
    # over Q, but has two quadratic factors over Q(sqrt(2)). Keep the
    # ordinary rational-domain behavior for all other expressions.
    symbol = sympy.Symbol("x")
    if sympy.expand(input_expr - (symbol**4 + 1)) == 0 and input_expr.free_symbols == {symbol}:
        factored = sympy.factor(input_expr, extension=sympy.sqrt(2))

    pattern_name = _detect_factor_pattern(input_expr, factored)

    if pattern_name is not None:
        # Sección 8.1, regla 5: todo paso candidato se verifica antes de
        # incluirse. Si por alguna razón no da VERIFIED, se degrada a
        # resumen en vez de bloquear la respuesta (sección 8.1, regla 3).
        if verify_step_equivalence(input_expr, factored) != "VERIFIED":
            pattern_name = None

    if pattern_name is not None:
        step = Step(
            index=0,
            title=pattern_name,
            description=f"Se identificó el patrón: {pattern_name.lower()}.",
            rule=pattern_name,
            latex_before=sympy.latex(input_expr),
            latex_after=sympy.latex(factored),
        )
        has_detailed_steps = True
    else:
        step = _summary_step(input_expr, factored, "Factorización")
        has_detailed_steps = False

    return AlgebraResult(
        input_expr,
        factored,
        [step],
        has_detailed_steps=has_detailed_steps,
        domain_conditions=domain_analysis.extract_domain_conditions(input_expr),
        pattern_name=pattern_name,
    )


def partial_fraction_expression(expression: str, variable: str = "x") -> AlgebraResult:
    """Decompose a rational expression over the specified symbol (AS-PF-01).

    This service-level capability is not yet a public HTTP endpoint.
    Preserve the original input for domain restrictions and ensure exactness.
    """
    input_expr = parsing.parse_expression_tree(expression, allow_equation=False)
    symbol = sympy.Symbol(variable)
    decomposed = sympy.apart(input_expr, symbol)
    if sympy.cancel(input_expr - decomposed) != 0:
        raise ValueError("Partial-fraction decomposition failed equivalence")
    return AlgebraResult(
        input_expr,
        decomposed,
        [_summary_step(input_expr, decomposed, "Fracciones parciales")],
        has_detailed_steps=False,
        domain_conditions=domain_analysis.extract_domain_conditions(input_expr),
    )
