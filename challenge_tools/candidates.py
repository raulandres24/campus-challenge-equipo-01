"""Funciones iniciales de Campus Challenge.

Revisa su comportamiento según los requisitos de la actividad.
"""
import math


def normalize_answer(answer):
    """Normaliza una respuesta para compararla sin distinguir mayúsculas."""
    return answer.strip().casefold()

def average_score(scores):
    """Devuelve la media aritmética de las puntuaciones."""
    if not scores:
        return 0.0
    return sum(scores) / len(scores)

def rotate_left(items, steps):
    """Devuelve una lista nueva rotada a la izquierda."""
    if not items:
        return []
    steps = steps % len(items)  # Soporta pasos negativos y mayores a la lista
    return items[steps:] + items[:steps]


def round_score_to_ten(score):
    """Redondea una puntuación no negativa a la decena más cercana; en la mitad exacta, redondea hacia arriba."""
    return math.floor(score / 10 + 0.5) * 10


def rank_teams(entries):
    """Ordena pares por puntuación descendente y resuelve empates alfabéticamente."""
    return sorted(entries, key=lambda item: (-item[1], item[0].casefold()))


def unique_tags(tags):
    """Elimina etiquetas repetidas conservando la primera aparición y el orden original."""
    result = []
    seen = set()

    for tag in tags:
        if tag not in seen:
            seen.add(tag)
            result.append(tag)

    return result

