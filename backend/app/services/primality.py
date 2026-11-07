"""AS-B-30: bounded primality answer for the frozen matrix `valor` row.

The matrix row is a yes/no question in Spanish. This module recognises only
two exact shapes (the frozen LaTeX question and a short functional form) and
answers with deterministic 64-bit Miller-Rabin. It is not a general
natural-language layer; anything else keeps following the ordinary parser.

Deterministic bases: the first twelve primes are a proven witness set for
every integer below 3.18e23, so 2**64-1 is fully covered.
"""

import re
from typing import Optional

MAX_PRIMALITY_VALUE = (1 << 64) - 1

_WITNESSES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)

_TEXT_QUERY = re.compile(r"^\s*\\text\{\s*¿es primo\s*\}\s*(\d+)\s*\?\s*$")
_CALL_QUERY = re.compile(r"^\s*(?:primo|esprimo)\s*\(\s*(\d+)\s*\)\s*$")


def parse_primality_query(expression: str) -> Optional[int]:
    """Return the queried integer for an exact recognised shape, else None."""
    match = _TEXT_QUERY.match(expression) or _CALL_QUERY.match(expression)
    if match is None:
        return None
    return int(match.group(1))


def is_prime(value: int) -> bool:
    """Deterministic Miller-Rabin, exact for every value <= 2**64-1."""
    if type(value) is not int or value < 2:
        return False
    for prime in _WITNESSES:
        if value % prime == 0:
            return value == prime
    remainder = value - 1
    shifts = 0
    while remainder % 2 == 0:
        remainder //= 2
        shifts += 1
    for base in _WITNESSES:
        candidate = pow(base, remainder, value)
        if candidate in (1, value - 1):
            continue
        for _ in range(shifts - 1):
            candidate = candidate * candidate % value
            if candidate == value - 1:
                break
        else:
            return False
    return True


def answer_for(value: int) -> str:
    """Exact answer text used by the matrix contract."""
    if value < 2:
        return "no, no es primo"
    if is_prime(value):
        return "sí, es primo"
    return "no, es compuesto"
