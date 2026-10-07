"""
reservas/niveles.py
===================
Qué salas puede reservar cada nivel académico. Es una función pura (sin base de datos).

Regla vigente (decisión provisional, 07/10/2026):

    - Salas B, C, D, F, H y J: solo estudiantes de pregrado.
    - Salas A y E (``exclusiva_posgrado``): solo postgrado y doctorado.

Pendiente de confirmar con el docente: si postgrado y doctorado, además de A y E,
pueden usar las demás salas. Si dice que sí, el cambio es una sola línea en
``nivel_puede_usar_sala``: ``return es_posgrado or not sala_exclusiva_posgrado``.
"""

from __future__ import annotations

NIVELES_POSGRADO = frozenset({"postgrado", "doctorado"})


def nivel_puede_usar_sala(nivel: str, sala_exclusiva_posgrado: bool) -> bool:
    """True si un estudiante de ese nivel puede reservar esa sala."""
    es_posgrado = (nivel or "").strip().lower() in NIVELES_POSGRADO
    return es_posgrado == bool(sala_exclusiva_posgrado)


def mensaje_sala_no_permitida(nivel: str, nombre_sala: str, sala_exclusiva_posgrado: bool) -> str:
    """Explica por qué ese nivel no puede reservar esa sala."""
    if sala_exclusiva_posgrado:
        return f"La {nombre_sala} es exclusiva de postgrado y doctorado. Tu nivel es {nivel or 'pregrado'}."
    return f"La {nombre_sala} es de pregrado. Tu nivel es {nivel}: usa las salas exclusivas de postgrado y doctorado."
