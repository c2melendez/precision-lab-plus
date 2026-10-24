from app.services import solve_service

def test_en_di_18_x_equals_3():
    result = solve_service.solve_equation("x=3", None, "rad")
    assert len(result.solutions) == 1
    assert result.solutions[0].text == "3"
