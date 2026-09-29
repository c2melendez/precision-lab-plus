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


def test_vertical_lines_are_real_traces_and_higher_dimensions_stay_advanced():
    vertical = solve(["x=1", "y=2"])
    assert vertical["result_data"]
    assert vertical["system_graph_expressions"] is None
    assert [(trace["type"], trace["x"]) for trace in vertical["graph_data"]["traces"]] == [
        ("line", [1.0, 1.0]), ("line", [-9.0, 11.0]), ("point", [1.0])]
    assert vertical["system_graph_intersections"] == [[1.0, 2.0]]

    parallel = solve(["x=1", "x=2"])
    assert len(parallel["graph_data"]["traces"]) == 2
    assert parallel["system_graph_intersections"] == []

    coincident = solve(["x=1", "2*x=2"])
    assert len(coincident["graph_data"]["traces"]) == 1
    assert coincident["system_graph_coincident"] is True

    higher = solve(["x=1", "y=2", "z=3"], ("x", "y", "z"))
    assert higher["system_graph_expressions"] is None
    assert higher["graph_data"] is None


def test_real_nonlinear_branches_and_exact_common_points():
    crossing = solve(["x**2+y**2=1", "y=x"])
    assert crossing["system_graph_expressions"] == [
        "-sqrt(1 - x**2)", "sqrt(1 - x**2)", "x"]
    assert crossing["system_graph_component_indices"] == [0, 0, 1]
    assert len(crossing["system_graph_intersections"]) == 2
    assert crossing["system_graph_intersections"][0][0] < 0
    assert crossing["system_graph_intersections"][1][0] > 0

    disjoint = solve(["x**2+y**2=1", "x**2+y**2=4"])
    assert disjoint["result_data"] == []
    assert len(disjoint["system_graph_expressions"]) == 4
    assert disjoint["system_graph_intersections"] == []

    coincident = solve(["x**2+y**2=1", "2*x**2+2*y**2=2"])
    assert coincident["system_graph_coincident"] is True
    assert coincident["system_graph_component_indices"] == [0, 0]
    assert coincident["system_graph_intersections"] == []

    implicit = solve(["x**2+y**2=1", "x=1"])
    assert implicit["result_data"]
    assert implicit["system_graph_expressions"] is None
    assert implicit["graph_data"] is None
