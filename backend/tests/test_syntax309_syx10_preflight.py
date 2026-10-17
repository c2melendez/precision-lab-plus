"""SY-X-10: astronomical nested powers must be guarded before evaluation."""
import json
from pathlib import Path
import pytest
import sympy as sp
from app.services.ast_validator import ComplexityLimitError, check_complexity_limits

def test_syx10_canonical_nested_integer_power_preflight_and_finite_control():
    rows = (Path(__file__).resolve().parents[2] / "qa/certification/syntax309_cases.jsonl").read_text().splitlines()
    case = next(json.loads(line) for line in rows if json.loads(line)["id"] == "SY-X-10")
    assert case["entrada"] == "10^{10^{10}}"
    assert case["esperado"] == "resultado simbólico o aviso de tamaño; sin intentar imprimir 10^10 dígitos"
    nested = sp.Pow(sp.Integer(10), sp.Integer(10), evaluate=False)
    source = sp.Pow(sp.Integer(10), nested, evaluate=False)
    with pytest.raises(ComplexityLimitError, match="Potencia anidada excede"):
        check_complexity_limits(source)
    check_complexity_limits(sp.Add(sp.Integer(2), sp.Integer(3), evaluate=False))
