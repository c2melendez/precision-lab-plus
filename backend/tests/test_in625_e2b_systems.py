from app.services.phase2_service import compute_solve_system

def test_en_mt_11_to_13_system_solution():
    result=compute_solve_system(["x+y=3","x-y=1"],["x","y"])
    assert result.has_solutions
    assert len(result.solutions)==1
    text=result.solutions[0].text.replace(" ","")
    assert "x=2" in text and "y=1" in text
