"""Suite exhaustiva original — Módulo 9: Graficación.

QA-only. No modifica código de producto.
"""
import math
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=False)

def post(path, payload):
    return client.post(f"/api/v1/{path}", json=payload)

def test_m9_graph2d_known_and_multiple_curves():
    b = post("graph/2d", {
        "expressions": ["x**2", "x"],
        "variable": "x",
        "x_min": -2,
        "x_max": 2,
        "samples": 201,
        "angle_unit": "rad",
    }).json()
    assert b["success"] is True, b
    traces = b["graph_data"]["traces"]
    assert len(traces) == 2
    assert all(t["type"] == "line" for t in traces)
    idx0 = min(range(len(traces[0]["x"])), key=lambda i: abs(traces[0]["x"][i]))
    assert traces[0]["x"][idx0] == pytest.approx(0, abs=1e-12)
    assert traces[0]["y"][idx0] == pytest.approx(0, abs=1e-12)

def test_m9_graph2d_discontinuity_breaks_trace():
    b = post("graph/2d", {
        "expressions": ["1/(x-2)"],
        "variable": "x",
        "x_min": 0,
        "x_max": 4,
        "samples": 201,
        "angle_unit": "rad",
    }).json()
    assert b["success"] is True, b
    trace = b["graph_data"]["traces"][0]
    assert any(y is None for y in trace["y"]), trace

def test_m9_graph3d_known_surface():
    b = post("graph/3d", {
        "expression": "x+y",
        "variables": ["x", "y"],
        "x_range": [-1, 1],
        "y_range": [-1, 1],
    }).json()
    assert b["success"] is True, b
    trace = b["graph_data"]["traces"][0]
    assert trace["type"] == "surface"
    assert len(trace["x"]) == 40
    assert len(trace["y"]) == 40
    assert len(trace["z"]) == 40
    assert len(trace["z"][0]) == 40
    assert trace["z"][0][0] == pytest.approx(-2, abs=1e-9)
    assert trace["z"][-1][-1] == pytest.approx(2, abs=1e-9)

def test_m9_parametric_unit_circle():
    b = post("graph/parametric", {
        "x_expression": "cos(t)",
        "y_expression": "sin(t)",
        "parameter": "t",
        "t_min": 0,
        "t_max": 2 * math.pi,
    }).json()
    assert b["success"] is True, b
    trace = b["graph_data"]["traces"][0]
    assert trace["type"] == "line"
    assert len(trace["x"]) >= 250
    assert trace["x"][0] == pytest.approx(1, abs=1e-9)
    assert trace["y"][0] == pytest.approx(0, abs=1e-9)
    assert trace["x"][-1] == pytest.approx(1, abs=1e-6)
    assert trace["y"][-1] == pytest.approx(0, abs=1e-6)

def test_m9_polar_unit_circle():
    b = post("graph/polar", {
        "r_expression": "1",
        "variable": "theta",
        "theta_min": 0,
        "theta_max": 2 * math.pi,
    }).json()
    assert b["success"] is True, b
    trace = b["graph_data"]["traces"][0]
    assert trace["type"] == "line"
    assert len(trace["x"]) >= 250
    assert trace["x"][0] == pytest.approx(1, abs=1e-9)
    assert trace["y"][0] == pytest.approx(0, abs=1e-9)

def test_m9_invalid_variable_is_explicit():
    b = post("graph/2d", {
        "expressions": ["x+y"],
        "variable": "x",
        "x_min": -2,
        "x_max": 2,
        "samples": 101,
        "angle_unit": "rad",
    }).json()
    assert b["success"] is False
    assert b["error_code"] == "INVALID_VARIABLE"
