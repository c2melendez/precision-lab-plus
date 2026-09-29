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
