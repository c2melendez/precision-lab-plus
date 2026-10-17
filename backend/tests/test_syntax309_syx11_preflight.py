"""SY-X-11 bounded preflight without calculating a gigantic integer."""
import json
from pathlib import Path
import pytest
import sympy as sp
from app.services.ast_validator import ComplexityLimitError, check_complexity_limits

def test_syx11_original_guard_and_finite_nested_power():
    lines=(Path(__file__).resolve().parents[2]/"qa/certification/syntax309_cases.jsonl").read_text().splitlines()
    row=next(json.loads(line) for line in lines if json.loads(line)["id"]=="SY-X-11")
    assert row["entrada"]=="9^{9^{9}}"
    assert row["esperado"]=="ídem (el número tiene unos 369 millones de dígitos)"
    inner=sp.Pow(sp.Integer(9),sp.Integer(9),evaluate=False)
    expression=sp.Pow(sp.Integer(9),inner,evaluate=False)
    with pytest.raises(ComplexityLimitError,match="Potencia anidada excede"):
        check_complexity_limits(expression)
    finite=sp.Pow(sp.Integer(2),sp.Pow(sp.Integer(3),sp.Integer(2),evaluate=False),evaluate=False)
    check_complexity_limits(finite)
