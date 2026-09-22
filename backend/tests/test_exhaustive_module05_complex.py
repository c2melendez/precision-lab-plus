"""Suite exhaustiva original — Módulo 5: Complejos y Argand.

QA-only. No modifica código de producto.
"""
import math
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=False)

def post(path, payload):
    return client.post(f"/api/v1/{path}", json=payload)

def test_m5_basic_complex_functions():
    cases = [
        ("re(3+4*i)", 3.0),
        ("im(3+4*i)", 4.0),
        ("arg(1+i)", math.pi/4),
        ("abs(3+4*i)", 5.0),
    ]
    for expr, expected in cases:
        r = post("evaluate", {"expression":expr,"angle_unit":"rad"})
        b = r.json()
        assert r.status_code == 200 and b["success"] is True, b
        assert b["result_approx"] == pytest.approx(expected, abs=1e-10), b

def test_m5_conjugate_polar_root_power():
    for expr in ["conj(3+4*i)", "topolar(3+4*i)", "root(-4,2)", "(1+i)^2"]:
        b = post("evaluate", {"expression":expr,"angle_unit":"rad"}).json()
        assert b["success"] is True, b
    root = post("evaluate", {"expression":"root(-4,2)","angle_unit":"rad"}).json()
    assert root["result_text"] == "2*I"

def test_m5_complex_log_uses_principal_natural_log():
    # Contrato actual: log(x) es log base 10 de calculadora; Log(z) es
    # el logaritmo complejo natural principal.
    b = post("evaluate", {"expression":"Log(-1)","angle_unit":"rad"}).json()
    assert b["success"] is True, b
    assert b["result_text"] == "I*pi", b

def test_m5_residue_and_singularities():
    r = post("complex/residue", {"expression":"1/(z-2)","point":"z=2"}).json()
    assert r["success"] is True and r["result_text"] == "1"

    s = post("complex/singularities", {"expression":"1/((z-1)*(z+2))"}).json()
    assert s["success"] is True and s["result_text"] == "{-2, 1}"

    inf = post("complex/singularities", {"expression":"1/sin(z)"}).json()
    assert inf["success"] is False and inf["error_code"] == "UNSUPPORTED_OPERATION"

def test_m5_argand_backend_point():
    b = post("graph/complex_point", {"expression":"3+4*i"}).json()
    assert b["success"] is True, b
    g = b["graph_data"]
    assert g["traces"][0]["type"] == "point"
    assert g["traces"][0]["x"] == [3.0]
    assert g["traces"][0]["y"] == [4.0]
    assert g["x_axis_label"] == "Re"
    assert g["y_axis_label"] == "Im"

    bad = post("graph/complex_point", {"expression":"z+1"}).json()
    assert bad["success"] is False and bad["error_code"] == "DOMAIN_ERROR"
