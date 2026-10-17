"""SY-X-12 exact fixture: never present an unresolved integral as a primitive."""
import json
from pathlib import Path
import sympy as sp
from unittest.mock import patch
from app.services import integral_service as svc

def test_syx12_canonical_integral_unevaluated_is_flagged_not_invented():
    rows=(Path(__file__).resolve().parents[2]/"qa/certification/syntax309_cases.jsonl").read_text().splitlines()
    case=next(json.loads(line) for line in rows if json.loads(line)["id"]=="SY-X-12")
    assert case["entrada"]==r"\\int\\sin\\left(x^{x}\\right)dx"
    assert case["esperado"]=="sin forma elemental: aviso claro; no una antiderivada inventada"
    x=sp.Symbol("x")
    integrand=sp.sin(x**x)
    unresolved=sp.Integral(integrand,x)
    with patch.object(svc.mi,"integral_steps",return_value=svc.mi.DontKnowRule(integrand,x)),patch.object(svc.sympy,"integrate",return_value=unresolved):
        value,steps,detailed,warnings=svc._compute_indefinite(integrand,x)
    assert value==unresolved
    assert not steps and not detailed
    assert any("Sin forma elemental" in message for message in warnings)
