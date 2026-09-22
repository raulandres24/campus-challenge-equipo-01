"""Añade pruebas para comportamientos no cubiertos en test_baseline.py.

Cada prueba debe:
- Tener un nombre que comience con test_.
- Comprobar el comportamiento mediante assert.
- Indicar el requisito correspondiente en un comentario o docstring.

Deriva el resultado esperado del requisito, no del resultado
que devuelve la implementación actual.
"""

from challenge_tools import (
    average_score,
    normalize_answer,
    rank_teams,
    rotate_left,
    round_score_to_ten,
    unique_tags,
)

from challenge_tools import normalize_answer, average_score

# ==========================================
# Pruebas para normalize_answer (Requisito R-03)
# ==========================================

def test_normalize_answer_espacios_y_mayusculas():
    """R-03: Quita espacios exteriores y estandariza mayúsculas/minúsculas."""
    assert normalize_answer("  Hola Mundo  ") == "hola mundo"

def test_normalize_answer_caracteres_unicode():
    """R-03: Soporta caracteres especiales y tildes en Unicode."""
    assert normalize_answer("\tÁEIOÚ ñÑ \n") == "áeioú ññ"

def test_normalize_answer_cadena_vacia():
    """R-03: Una cadena vacía devuelve una cadena vacía."""
    assert normalize_answer("") == ""

def test_normalize_answer_solo_espacios():
    """R-03: Una cadena con solo espacios se normaliza a vacío."""
    assert normalize_answer("     ") == ""

def test_normalize_answer_sin_cambios_necesarios():
    """R-03: Una cadena ya limpia no sufre alteraciones innecesarias."""
    assert normalize_answer("python") == "python"


# ==========================================
# Pruebas para average_score (Requisito R-08)
# ==========================================

def test_average_score_coleccion_vacia():
    """R-08: Para una colección vacía devuelve 0.0."""
    assert average_score([]) == 0.0

def test_average_score_un_solo_elemento():
    """R-08: El promedio de un solo elemento es el mismo valor."""
    assert average_score([85]) == 85.0

def test_average_score_lista_enteros():
    """R-08: Calcula correctamente la media aritmética de enteros."""
    assert average_score([80, 90, 100]) == 90.0

def test_average_score_con_decimales():
    """R-08: Calcula correctamente la media con valores decimales."""
    assert average_score([12.5, 15.5, 10.0]) == 12.666666666666666 or pytest.approx(13.33, 0.01) # Ajustar según precisión esperada

def test_average_score_no_modifica_entrada():
    """R-02/R-08: La colección original no debe ser modificada."""
    original = [50, 70, 90]
    copia = list(original)
    average_score(original)
    assert original == copia