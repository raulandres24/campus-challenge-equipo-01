"""
reservas/agenda.py
==================
Arma la agenda del día (bloques horarios × salas) para las plantillas.

Es una función pura: no consulta la base de datos, por eso se prueba sin MongoDB.

Una reserva aparece en **todos** los bloques con los que se cruza. Así se ve
aunque no empiece justo al inicio de un bloque (por ejemplo, una reserva
movida a 08:00–09:30 aparece en el bloque 07:45–09:45).
"""

from __future__ import annotations


def _minutos(hhmm: str) -> int:
    horas, minutos = hhmm.split(":")
    return int(horas) * 60 + int(minutos)


def _se_cruzan(reserva: dict, bloque: dict) -> bool:
    return (
        _minutos(reserva["hora_inicio"]) < _minutos(bloque["fin"])
        and _minutos(reserva["hora_fin"]) > _minutos(bloque["inicio"])
    )


def armar_agenda(salas, reservas: list[dict], bloques: list[dict]) -> tuple[list[dict], list[dict]]:
    """Devuelve dos vistas de la misma agenda.

    Parámetros:
        salas:    objetos con ``nombre`` y ``en_mantenimiento``.
        reservas: diccionarios con ``sala_nombre``, ``hora_inicio`` y ``hora_fin`` ("HH:MM").
        bloques:  diccionarios con ``inicio``, ``fin`` y ``label``.

    Retorna:
        filas:    una fila por bloque, con una celda por sala (tabla de escritorio).
        por_sala: una entrada por sala, con sus bloques (lista para celular).

    Cada celda es ``{"sala", "bloque", "reservas": [...], "libre": bool}``;
    ``libre`` es True solo si la sala no está en mantenimiento y no hay reservas.
    """
    celdas = {}
    for sala in salas:
        for bloque in bloques:
            del_bloque = [
                r for r in reservas
                if r["sala_nombre"] == sala.nombre and _se_cruzan(r, bloque)
            ]
            celdas[(sala.nombre, bloque["inicio"])] = {
                "sala": sala,
                "bloque": bloque,
                "reservas": del_bloque,
                "libre": not sala.en_mantenimiento and not del_bloque,
            }

    filas = [
        {"bloque": b, "celdas": [celdas[(s.nombre, b["inicio"])] for s in salas]}
        for b in bloques
    ]
    por_sala = [
        {"sala": s, "celdas": [celdas[(s.nombre, b["inicio"])] for b in bloques]}
        for s in salas
    ]
    return filas, por_sala
