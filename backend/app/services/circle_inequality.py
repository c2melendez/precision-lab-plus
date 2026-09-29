"""Certified real circular regions for direct two-variable inequalities."""

import math
from typing import Optional

import sympy


def circle_region(expr: sympy.Expr, operator: str) -> Optional[dict]:
    """Recognize a nondegenerate circle; leave other conics to advanced graphing."""
    x, y = sympy.symbols("x y")
    try:
        polynomial = sympy.Poly(expr, x, y)
    except sympy.PolynomialError:
        return None
    if polynomial.total_degree() != 2:
        return None
    a = polynomial.coeff_monomial(x ** 2)
    if a == 0 or polynomial.coeff_monomial(y ** 2) != a or polynomial.coeff_monomial(x * y) != 0:
        return None
    bx, by = polynomial.coeff_monomial(x), polynomial.coeff_monomial(y)
    constant = polynomial.coeff_monomial(1)
    if any(coefficient.is_real is not True for coefficient in (a, bx, by, constant)):
        return None
    cx, cy = -bx / (2 * a), -by / (2 * a)
    radius_squared = sympy.simplify(cx ** 2 + cy ** 2 - constant / a)
    if radius_squared.is_positive is not True:
        return None
    try:
        center_x, center_y, radius = float(cx), float(cy), float(sympy.sqrt(radius_squared))
    except (TypeError, ValueError, OverflowError):
        return None
    if not all(math.isfinite(value) and abs(value) < 1e5 for value in (center_x, center_y, radius)):
        return None
    if radius < 1e-6 or radius > 1e4:
        return None
    normalized = operator if a.is_positive else {"<": ">", "<=": ">=", ">": "<", ">=": "<="}[operator]
    return {
        "center_x": center_x, "center_y": center_y, "radius": radius,
        "center_x_exact": str(cx), "center_y_exact": str(cy),
        "radius_exact": str(sympy.sqrt(radius_squared)),
        "inside": normalized in ("<", "<="), "boundary_included": normalized in ("<=", ">="),
    }


def ellipse_region(expr: sympy.Expr, operator: str) -> Optional[dict]:
    """Recognize a real axis-aligned ellipse, excluding circles and rotated conics."""
    x, y = sympy.symbols("x y")
    try:
        polynomial = sympy.Poly(expr, x, y)
    except sympy.PolynomialError:
        return None
    if polynomial.total_degree() != 2 or polynomial.coeff_monomial(x * y) != 0:
        return None
    a, b = polynomial.coeff_monomial(x ** 2), polynomial.coeff_monomial(y ** 2)
    if a == 0 or b == 0 or a == b or a.is_positive is None or b.is_positive != a.is_positive:
        return None
    bx, by = polynomial.coeff_monomial(x), polynomial.coeff_monomial(y)
    constant = polynomial.coeff_monomial(1)
    if any(coefficient.is_real is not True for coefficient in (a, b, bx, by, constant)):
        return None
    cx, cy = -bx / (2 * a), -by / (2 * b)
    level = sympy.simplify(-constant + bx ** 2 / (4 * a) + by ** 2 / (4 * b))
    rx_squared, ry_squared = sympy.simplify(level / a), sympy.simplify(level / b)
    if rx_squared.is_positive is not True or ry_squared.is_positive is not True:
        return None
    rx, ry = sympy.sqrt(rx_squared), sympy.sqrt(ry_squared)
    try:
        center_x, center_y, radius_x, radius_y = map(float, (cx, cy, rx, ry))
    except (TypeError, ValueError, OverflowError):
        return None
    if not all(math.isfinite(value) and abs(value) < 1e5 for value in
               (center_x, center_y, radius_x, radius_y)):
        return None
    if min(radius_x, radius_y) < 1e-6 or max(radius_x, radius_y) > 1e4:
        return None
    normalized = operator if a.is_positive else {"<": ">", "<=": ">=", ">": "<", ">=": "<="}[operator]
    return {
        "center_x": center_x, "center_y": center_y,
        "radius_x": radius_x, "radius_y": radius_y,
        "center_x_exact": str(cx), "center_y_exact": str(cy),
        "radius_x_exact": str(rx), "radius_y_exact": str(ry),
        "inside": normalized in ("<", "<="), "boundary_included": normalized in ("<=", ">="),
    }
