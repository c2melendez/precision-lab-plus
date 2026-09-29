"""B7: feasible regions and boundary inclusion share one canonical payload."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def solve(rows):
    response = client.post("/api/v1/inequality/system", json={
        "inequalities": rows, "variables": ["x", "y"]})
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    return body


def test_bounded_region_retains_open_and_closed_boundaries():
    result = solve(["x>0", "y>=0", "x+y<4"])
    assert result["inequality_region_kind"] == "bounded"
    assert [part["operator"] for part in result["inequality_constraints"]] == [">", ">=", "<"]
    assert len(result["inequality_preview_polygon"]) == 3
    assert len(result["result_data"]) == 3


def test_empty_strict_intersection_and_unbounded_halfplane():
    empty = solve(["x>0", "x<0"])
    assert empty["inequality_region_kind"] == "empty"
    assert empty["inequality_preview_polygon"] == []
    assert empty["result_data"] is None

    open_halfplane = solve(["x>0"])
    assert open_halfplane["inequality_region_kind"] == "unbounded"
    assert open_halfplane["inequality_preview_polygon"]
    assert open_halfplane["inequality_constraints"][0]["operator"] == ">"


def test_lower_dimensional_region_avoids_false_area_fill():
    line = solve(["x>=0", "x<=0", "y>0"])
    assert line["inequality_region_kind"] == "unbounded"
    assert line["inequality_preview_polygon"] is None
