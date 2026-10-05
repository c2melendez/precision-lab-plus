from app.services import solve_service

def test_en_di_22_equation_roots_before_constraint():
    result = solve_service.solve_equation("x**2-4=0", "x", "rad")
    roots = sorted(float(solution.text) for solution in result.solutions)
    assert roots == [-2.0, 2.0]
    assert [root for root in roots if root > 0] == [2.0]
