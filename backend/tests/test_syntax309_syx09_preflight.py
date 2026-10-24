"""SY-X-09 preflight: prove that the canonical extreme power is rejected before evaluation.

This deliberately constructs only an unevaluated AST: no large integer is computed,
serialized, printed or submitted to an unbounded HTTP worker.
"""
import json
from pathlib import Path

import pytest
import sympy as sp

from app.services.ast_validator import (
    MAX_ABS_INTEGER_EXPONENT,
    ComplexityLimitError,
    check_complexity_limits,
)


def test_syx09_original_contract_and_pre_evaluation_exponent_guard():
    rows = (Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl").read_text().splitlines()
    case = next(json.loads(line) for line in rows if json.loads(line)["id"] == "SY-X-09")
    assert case["entrada"] == "99999999999^{99999999999}"
    assert case["esperado"] == "límite de tiempo o memoria anunciado; nunca bloqueo ni valor falso"

    base, exponent = 99999999999, 99999999999
    assert exponent > MAX_ABS_INTEGER_EXPONENT
    expression = sp.Pow(sp.Integer(base), sp.Integer(exponent), evaluate=False)
    assert expression.is_Pow
    with pytest.raises(ComplexityLimitError, match="Exponente entero fuera de rango"):
        check_complexity_limits(expression)


def test_syx09_finite_control_remains_within_budget():
    expression = sp.Add(sp.Integer(2), sp.Integer(3), evaluate=False)
    check_complexity_limits(expression)
    assert sp.simplify(expression) == 5
