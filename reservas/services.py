"""
reservas/services.py
====================
Capa de servicios: toda la lógica de negocio del sistema de reservas UPB.

Principio de diseño:
  - reservar_si_esta_disponible  →  orquestador principal (public API)
  - _verificar_*                 →  una regla de negocio por función (private)

Cada función privada lanza ReservaRechazada si la regla falla,
lo que permite al orquestador ser declarativo y fácil de leer.
"""

from __future__ import annotations

import datetime

from .models import Estudiante, Reserva, Sala


# ---------------------------------------------------------------------------
# Excepción de dominio
# ---------------------------------------------------------------------------

class ReservaRechazada(Exception):
    """Se lanza cuando una regla de negocio impide crear la reserva."""


# ---------------------------------------------------------------------------
# Helpers privados — una función = una regla de negocio
# ---------------------------------------------------------------------------

def _verificar_estudiante_habilitado(estudiante: Estudiante) -> None:
    """Regla 1: El estudiante debe estar activo y con matrícula pagada."""
    if not estudiante.esta_activo:
        raise ReservaRechazada(
            f"El estudiante '{estudiante}' no está activo en el sistema."
        )
    if not estudiante.matricula_pagada:
        raise ReservaRechazada(
            f"El estudiante '{estudiante}' no tiene la matrícula pagada."
        )


def _verificar_sala_disponible(sala: Sala) -> None:
    """Regla 2: La sala no debe estar en mantenimiento."""
    if sala.en_mantenimiento:
        raise ReservaRechazada(
            f"La sala '{sala.nombre}' está en mantenimiento y no puede reservarse."
        )


def _verificar_una_reserva_por_dia(
    estudiante: Estudiante,
    fecha: datetime.date,
    hora_inicio: datetime.time,
    hora_fin: datetime.time,
) -> None:
    """Regla 3: El estudiante solo puede tener una reserva confirmada por día."""
    candidata = Reserva(
        estudiante=estudiante,
        sala_id=None,  # No importa la sala para esta regla
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
    )
    reservas_del_dia = Reserva.objects.filter(
        estudiante=estudiante,
        fecha=fecha,
        estado=Reserva.ESTADO_CONFIRMADA,
    )
    for existente in reservas_del_dia:
        if candidata.solapa_estudiante(existente):
            raise ReservaRechazada(
                "El estudiante ya cuenta con un espacio reservado en ese horario."
            )


def _verificar_disponibilidad_sala(
    sala: Sala,
    fecha: datetime.date,
    hora_inicio: datetime.time,
    hora_fin: datetime.time,
) -> None:
    """Regla 4 (Regla de oro): Valida solapamientos con buffer de 15 minutos.

    Crea una reserva temporal (no guardada) para aprovechar los helpers
    de solapamiento definidos en el modelo, evitando duplicar lógica.
    """
    candidata = Reserva(
        sala=sala,
        estudiante_id=None,  # No importa el estudiante para esta regla
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
    )
    reservas_activas = Reserva.objects.filter(
        sala=sala,
        fecha=fecha,
        estado=Reserva.ESTADO_CONFIRMADA,
    )
    for existente in reservas_activas:
        if candidata.choca_con(existente):
            raise ReservaRechazada(
                f"La sala '{sala.nombre}' no está disponible en ese horario "
                f"(se requieren {Reserva.BUFFER_MINUTOS} minutos de margen "
                f"entre reservas)."
            )


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

def reservar_si_esta_disponible(
    *,
    estudiante: Estudiante,
    sala: Sala,
    fecha: datetime.date,
    hora_inicio: datetime.time,
    hora_fin: datetime.time,
) -> Reserva:
    """Orquestador principal: valida todas las reglas y guarda la reserva.

    Parámetros con keyword-only (PEP 3102) para mayor claridad en el llamador.

    Retorna:
        La instancia de Reserva recién creada y guardada en BD.

    Lanza:
        ReservaRechazada  si alguna regla de negocio falla.
        ValueError        si hora_fin <= hora_inicio.
    """
    if hora_fin <= hora_inicio:
        raise ValueError("La hora de fin debe ser posterior a la hora de inicio.")

    # Cada helper valida UNA regla y lanza ReservaRechazada si falla.
    _verificar_estudiante_habilitado(estudiante)
    _verificar_sala_disponible(sala)
    _verificar_una_reserva_por_dia(estudiante, fecha, hora_inicio, hora_fin)
    _verificar_disponibilidad_sala(sala, fecha, hora_inicio, hora_fin)

    # Todas las reglas pasaron: persistir.
    reserva = Reserva.objects.create(
        estudiante=estudiante,
        sala=sala,
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        estado=Reserva.ESTADO_CONFIRMADA,
    )
    return reserva
