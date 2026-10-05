from app.services import matrix_service

def _m(rows):
    return matrix_service.parse_matrix([[str(x) for x in r] for r in rows])

def test_en_mt_03_and_04_determinant():
    assert matrix_service.determinant(_m([[1,2],[3,4]])).value == -2

def test_en_mt_05_inverse():
    assert matrix_service.inverse(_m([[1,2],[3,4]])).result_matrix.tolist() == [[-2,1],[matrix_service.sympy.Rational(3,2),matrix_service.sympy.Rational(-1,2)]]

def test_en_mt_06_power():
    assert matrix_service.power(_m([[1,2],[3,4]]),2).result_matrix.tolist() == [[7,10],[15,22]]

def test_en_mt_07_transpose():
    assert matrix_service.transpose(_m([[1,2],[3,4]])).result_matrix.tolist() == [[1,3],[2,4]]

def test_en_mt_08_matrix_vector_product():
    assert matrix_service.multiply(_m([[1,2],[3,4]]),_m([[1],[1]])).result_matrix.tolist() == [[3],[7]]
