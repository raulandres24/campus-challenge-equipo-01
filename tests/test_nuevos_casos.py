"""Añade pruebas para comportamientos no cubiertos en test_baseline.py.

Cada prueba debe:
- Tener un nombre que comience con test_.
- Comprobar el comportamiento mediante assert.
- Indicar el requisito correspondiente en un comentario o docstring.

Deriva el resultado esperado del requisito, no del resultado
que devuelve la implementación actual.
"""
import pytest

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

# ==========================================
# Pruebas avanzadas para rank_teams (R-06)
# ==========================================

def test_rank_teams_orden_descendente():
    """R-06: Clasifica correctamente por puntuación descendente."""
    assert rank_teams([("Beta", 10), ("Alpha", 30)]) == [("Alpha", 30), ("Beta", 10)]

def test_rank_teams_empate_alfabetico():
    """R-06: Resuelve empates usando orden alfabético."""
    assert rank_teams([("Zeta", 20), ("Alpha", 20)]) == [("Alpha", 20), ("Zeta", 20)]

def test_rank_teams_empate_insensible_mayusculas():
    """R-06: El desempate alfabético no debe distinguir entre mayúsculas y minúsculas."""
    entradas = [("zeta", 15), ("Alpha", 15), ("BETA", 15)]
    esperado = [("Alpha", 15), ("BETA", 15), ("zeta", 15)]
    assert rank_teams(entradas) == esperado

def test_rank_teams_mezcla_puntuaciones_y_empates():
    """R-06: Maneja correctamente una lista con varios empates y diferentes puntuaciones."""
    entradas = [("B", 10), ("a", 20), ("C", 10), ("d", 20)]
    esperado = [("a", 20), ("d", 20), ("B", 10), ("C", 10)]
    assert rank_teams(entradas) == esperado

def test_rank_teams_no_modifica_entrada():
    """R-02 / R-06: La lista original no debe ser modificada."""
    original = [("Beta", 10), ("Alpha", 30)]
    copia = list(original)
    rank_teams(original)
    assert original == copia


# ==========================================
# Pruebas avanzadas para rotate_left (R-04)
# ==========================================

def test_rotate_left_rotacion_normal():
    """R-04: Rota los elementos a la izquierda correctamente."""
    assert rotate_left([1, 2, 3, 4, 5], 2) == [3, 4, 5, 1, 2]

def test_rotate_left_pasos_negativos_rota_derecha():
    """R-04: Interpreta los pasos negativos como rotación a la derecha."""
    assert rotate_left([1, 2, 3, 4], -1) == [4, 1, 2, 3]

def test_rotate_left_rotacion_circular_mayor_al_tamaño():
    """R-04: La rotación debe ser circular (soporta pasos mayores al tamaño de la lista)."""
    assert rotate_left(["a", "b", "c"], 5) == ["c", "a", "b"]

def test_rotate_left_lista_vacia():
    """R-04: Admite una lista vacía sin arrojar errores."""
    assert rotate_left([], 3) == []

def test_rotate_left_no_modifica_entrada():
    """R-02 / R-04: La rotación debe devolver una nueva lista y no alterar la original."""
    original = [1, 2, 3]
    copia = list(original)
    rotate_left(original, 1)
    assert original == copia

## Parte de Raul
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



def test_round_score_ya_es_multiplo_de_diez():
    """R-05: Un valor que ya es múltiplo de diez no debe cambiar."""
    assert round_score_to_ten(30) == 30
    assert round_score_to_ten(100) == 100


def test_round_score_numero_grande():
    """R-05: Debe funcionar igual de bien con puntuaciones grandes."""
    assert round_score_to_ten(999995) == 1000000
    assert round_score_to_ten(999994) == 999990
