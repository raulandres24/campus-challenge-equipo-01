from challenge_tools import round_score_to_ten


def test_round_score_hacia_abajo():
    """R-05: Redondea hacia la decena inferior cuando termina en 1, 2, 3 o 4."""
    assert round_score_to_ten(24) == 20
    assert round_score_to_ten(21) == 20


def test_round_score_hacia_arriba():
    """R-05: Redondea hacia la decena superior cuando termina en 6, 7, 8 o 9."""
    assert round_score_to_ten(26) == 30
    assert round_score_to_ten(29) == 30


def test_round_score_mitad_exacta_siempre_arriba():
    """R-05: Si está a la mitad exacta (termina en 5), SIEMPRE redondea hacia arriba."""
    assert round_score_to_ten(5) == 10
    assert round_score_to_ten(15) == 20
    assert round_score_to_ten(25) == 30
    assert round_score_to_ten(35) == 40


def test_round_score_cero():
    """R-05: El 0 es un entero no negativo válido y debe devolver 0."""
    assert round_score_to_ten(0) == 0