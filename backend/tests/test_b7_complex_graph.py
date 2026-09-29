"""B7: Argand coordinates come from symbolic results, never rendered text."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_concrete_complex_number_and_symbolic_function():
    point = client.post("/api/v1/evaluate", json={"expression": "3+4i"}).json()
    assert point["success"] is True
    assert point["complex_graph_points"] == [{"re": 3.0, "im": 4.0, "label": "3 + 4*I"}]
    function = client.post("/api/v1/evaluate", json={"expression": "exp(I*x)"}).json()
    assert function["success"] is True
    assert function["complex_graph_points"] is None
    assert function["complex_graph_components"]["variable"] == "x"
    assert function["complex_graph_components"]["re_expression"] == "cos(x)"
    assert function["complex_graph_components"]["im_expression"] == "sin(x)"
    curves = client.post("/api/v1/graph/2d", json={
        "expressions": [function["complex_graph_components"]["re_expression"],
                        function["complex_graph_components"]["im_expression"]], "variable": "x",
    }).json()
    assert curves["success"] is True
    assert len(curves["graph_data"]["traces"]) == 2
    genuine_complex_variable = client.post("/api/v1/evaluate", json={"expression": "z^2+I*z"}).json()
    assert genuine_complex_variable["complex_graph_components"] is None
    for expression in ("sec(0)", "csc(pi/2)"):
        real = client.post("/api/v1/evaluate", json={"expression": expression})
        assert real.status_code == 200
        assert real.json()["complex_graph_points"] is None


def test_complex_roots_include_real_roots_in_the_same_plane():
    roots = client.post("/api/v1/solve", json={"equation": "x^2+1=0"}).json()
    assert roots["success"] is True
    assert {(p["re"], p["im"]) for p in roots["complex_graph_points"]} == {(0.0, 1.0), (0.0, -1.0)}
    mixed = client.post("/api/v1/solve", json={"equation": "x^3-1=0"}).json()
    assert mixed["success"] is True
    assert len(mixed["complex_graph_points"]) == 3
    assert any(p["re"] == 1 and p["im"] == 0 for p in mixed["complex_graph_points"])
    real = client.post("/api/v1/solve", json={"equation": "x^2-1=0"}).json()
    assert real["success"] is True
    assert real["complex_graph_points"] is None


def test_genuine_complex_variable_mapping_samples_do_not_claim_a_2d_curve():
    mapped = client.post("/api/v1/evaluate", json={"expression": "z^2"}).json()
    assert mapped["success"] is True
    assert mapped["complex_graph_components"] is None
    samples = mapped["complex_graph_mapping"]
    assert len(samples) == 4
    assert next(s for s in samples if s["source"]["label"] == "i")["target"] == {
        "re": -1.0, "im": 0.0, "label": "f(i)",
    }
    reciprocal = client.post("/api/v1/evaluate", json={"expression": "1/z"}).json()
    assert reciprocal["success"] is True
    assert {s["source"]["label"] for s in reciprocal["complex_graph_mapping"]} == {"1", "i", "1+i"}
