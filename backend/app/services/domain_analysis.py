"""Domain restrictions derived from the ORIGINAL SymPy tree.

The calculator must not lose exclusions when an algebraic transformation
cancels the syntax that made them visible. Example:

    (x**2 - 1)/(x - 1)  ->  x + 1

The transformed expression is x+1, but the source expression is undefined
at x=1. These helpers inspect the evaluate=False parse tree before any
simplification and return explicit, serializable restrictions.
"""

from __future__ import annotations

from typing import Iterable, List

import sympy

from app.schemas.responses import DomainCondition


def _finite_nonzero_conditions(base: sympy.Expr) -> Iterable[sympy.Rel]:
    """Prefer x != root for simple univariate denominators.

    For expressions that are not a small polynomial, retain the structural
    condition base != 0 rather than spending unbounded time solving it.
    """
    symbols = list(base.free_symbols)
    if len(symbols) == 1:
        variable = symbols[0]
        try:
            poly = sympy.Poly(base, variable)
            if poly.degree() <= 4:
                roots = sympy.solveset(
                    sympy.Eq(base, 0), variable, domain=sympy.S.Reals
                )
                if isinstance(roots, sympy.FiniteSet):
                    for root in sorted(roots, key=str):
                        yield sympy.Ne(variable, root, evaluate=False)
                    return
        except (sympy.PolynomialError, NotImplementedError, ValueError):
            pass
    yield sympy.Ne(base, 0, evaluate=False)


def _condition_to_model(condition: sympy.Rel, kind: str) -> DomainCondition:
    # Canonicalize only the restriction itself for display. The source
    # expression tree remains untouched; this merely turns forms such as
    # x - 1*2 > 0 into the clearer equivalent x > 2.
    canonical = sympy.simplify(condition)
    symbols = sorted(canonical.free_symbols, key=lambda symbol: str(symbol))
    variable = str(symbols[0]) if len(symbols) == 1 else None
    return DomainCondition(
        text=str(canonical),
        latex=sympy.latex(canonical),
        variable=variable,
        kind=kind,
    )


def extract_domain_conditions(expr: sympy.Expr) -> List[DomainCondition]:
    """Extract real-domain conditions without transforming expr.

    Covered structural sources:
    - negative powers / denominators -> denominator != 0;
    - logarithms -> argument > 0 (and any denominator introduced by a
      change-of-base form is handled independently);
    - even-index rational powers -> radicand >= 0, or > 0 when exponent is
      negative;
    - asin/acos -> -1 <= argument <= 1;
    - acosh -> argument >= 1;
    - atanh -> -1 < argument < 1.

    The list is additive and best-effort. It never changes the mathematical
    result and never infers conditions from the already simplified output.
    """
    collected: list[tuple[sympy.Rel, str]] = []

    for node in sympy.preorder_traversal(expr):
        if isinstance(node, sympy.Pow):
            base, exponent = node.as_base_exp()

            if exponent.is_negative is True:
                collected.extend(
                    (condition, "denominator")
                    for condition in _finite_nonzero_conditions(base)
                )

            if isinstance(exponent, sympy.Rational) and exponent.q % 2 == 0:
                relation = (
                    sympy.Gt(base, 0, evaluate=False)
                    if exponent.is_negative is True
                    else sympy.Ge(base, 0, evaluate=False)
                )
                collected.append((relation, "even_root"))

        if getattr(node, "func", None) == sympy.log and node.args:
            collected.append(
                (sympy.Gt(node.args[0], 0, evaluate=False), "log")
            )

        if getattr(node, "func", None) in (sympy.asin, sympy.acos) and node.args:
            arg = node.args[0]
            collected.append(
                (sympy.Ge(arg, -1, evaluate=False), "inverse_trig")
            )
            collected.append(
                (sympy.Le(arg, 1, evaluate=False), "inverse_trig")
            )

        if getattr(node, "func", None) == sympy.acosh and node.args:
            collected.append(
                (
                    sympy.Ge(node.args[0], 1, evaluate=False),
                    "inverse_hyperbolic",
                )
            )

        if getattr(node, "func", None) == sympy.atanh and node.args:
            arg = node.args[0]
            collected.append(
                (sympy.Gt(arg, -1, evaluate=False), "inverse_hyperbolic")
            )
            collected.append(
                (sympy.Lt(arg, 1, evaluate=False), "inverse_hyperbolic")
            )

    seen: set[str] = set()
    result: List[DomainCondition] = []
    for condition, kind in collected:
        # Las restricciones persistentes describen el dominio simbólico.
        # Una condición constante verdadera como 2 != 0, log(100)>0 o
        # 9>=0 no aporta información y, peor, puede desplazar visualmente
        # el resultado. Las constantes inválidas ya son responsabilidad
        # del evaluador/operación normal (DOMAIN_ERROR).
        if not condition.free_symbols:
            continue
        key = sympy.srepr(condition)
        if key in seen:
            continue
        seen.add(key)
        result.append(_condition_to_model(condition, kind))

    result.sort(key=lambda item: (item.variable or "", item.kind, item.text))
    summary = real_domain_summary(expr) if result else None
    if summary is not None:
        result.append(summary)
    return result


def _set_text(domain: sympy.Set, var: sympy.Symbol) -> tuple[str, str] | None:
    """SymPy-parsable relational for the real domain, e.g. Ne(x, -1) & Ne(x, 1)."""
    complement = sympy.S.Reals - domain
    if isinstance(complement, sympy.FiniteSet) and complement:
        relation = sympy.And(*(sympy.Ne(var, p) for p in sorted(complement, key=float)))
    else:
        parts = domain.args if isinstance(domain, sympy.Union) else (domain,)
        pieces = []
        for part in parts:
            if not isinstance(part, sympy.Interval):
                return None
            bounds = []
            if part.start != -sympy.oo:
                bounds.append(var > part.start if part.left_open else var >= part.start)
            if part.end != sympy.oo:
                bounds.append(var < part.end if part.right_open else var <= part.end)
            if not bounds:
                return None
            pieces.append(sympy.And(*bounds))
        relation = sympy.Or(*pieces)
    return str(relation), sympy.latex(relation)


def real_domain_summary(expr: sympy.Expr) -> DomainCondition | None:
    """Algebra114 AS-DOM: combined real domain of a univariate ORIGINAL expression."""
    symbols = list(expr.free_symbols)
    if len(symbols) != 1:
        return None
    var = symbols[0]
    try:
        from sympy.calculus.util import continuous_domain

        domain = continuous_domain(expr, var, sympy.S.Reals)
        if domain == sympy.S.Reals or domain is sympy.S.EmptySet:
            return None
        rendered = _set_text(domain, var)
    except Exception:
        return None
    if rendered is None:
        return None
    return DomainCondition(text=rendered[0], latex=rendered[1], variable=str(var), kind="domain")
