from app.services import phase2_service

def test_en_di_07_to_11_same_linear_system():
    result = phase2_service.compute_solve_system(["x+y=3", "x-y=1"], ["x", "y"])
    assert result.has_solutions is True
    assert len(result.solutions) == 1
    assert result.solutions[0].text == "x=2, y=1"
