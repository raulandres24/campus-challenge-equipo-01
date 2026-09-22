"""Funciones iniciales de Campus Challenge.

Revisa su comportamiento según los requisitos de la actividad.
"""


def normalize_answer(answer):
    """Normaliza una respuesta para compararla sin distinguir mayúsculas."""
    return answer.strip().casefold()


def rotate_left(items, steps):
    """Devuelve una lista nueva rotada a la izquierda."""
    copied = list(items)
    copied.rotate(-steps)
    return copied


def round_score_to_ten(score):
    """Redondea una puntuación no negativa a la decena más cercana."""
    return round(score / 10) * 10


def rank_teams(entries):
    """Ordena pares (equipo, puntuación) para la clasificación."""
    return sorted(entries, key=lambda item: -item[1])


def unique_tags(tags):
    """Elimina etiquetas repetidas."""
    return list(set(tags))


def average_score(scores):
    """Devuelve la media aritmética de las puntuaciones."""
    return sum(scores) / len(scores)