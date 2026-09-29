"""B7: only certified explicit affine system curves reach the graph bridge."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def solve(equations, variables=("x", "y")):
    response = client.post("/api/v1/solve/system", json={"equations": equations, "variables": variables})
    assert response.status_code == 200
    return response.json()


def test_intersection_parallel_and_coincident_lines():
    crossing = solve(["x+y=3", "x-y=1"])
    assert crossing["system_graph_expressions"] == ["3 - x", "x - 1"]
    assert crossing["system_graph_intersections"] == [[2.0, 1.0]]
    assert len(crossing["result_data"]) == 1

    parallel = solve(["x+y=3", "x+y=4"])
    assert parallel["result_data"] == []
    assert parallel["system_graph_expressions"] == ["3 - x", "4 - x"]
    assert parallel["system_graph_intersections"] == []

    coincident = solve(["x+y=3", "2*x+2*y=6"])
    assert coincident["system_graph_expressions"] == ["3 - x"]
    assert coincident["system_graph_coincident"] is True
    assert coincident["system_graph_intersections"] == []


def test_vertical_and_higher_dimensional_systems_have_no_cartesian_certificate():
    vertical = solve(["x=1", "y=2"])
    assert vertical["result_data"]
    assert vertical["system_graph_expressions"] is None

    higher = solve(["x=1", "y=2", "z=3"], ("x", "y", "z"))
    assert higher["system_graph_expressions"] is None
