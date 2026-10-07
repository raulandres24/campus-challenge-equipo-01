"""
reservas/services.py
====================
Capa de servicios: toda la lógica de negocio del sistema de reservas UPB.

Principio de diseño:
  - reservar_si_esta_disponible           →  orquestador para crear (public API)
  - modificar_reserva_si_esta_disponible  →  orquestador para modificar (RES-05, RES-CU-01)
  - _verificar_*                          →  una regla de negocio por función (private)

Cada función privada lanza ReservaRechazada si la regla falla,
lo que permite al orquestador ser declarativo y fácil de leer.
"""

from __future__ import annotations

import datetime
from typing import Optional

from django.utils import timezone

from .models import Estudiante, Reserva, Sala


# ---------------------------------------------------------------------------
# Excepción de dominio
# ---------------------------------------------------------------------------

class ReservaRechazada(Exception):
    """Se lanza cuando una regla de negocio impide crear o modificar la reserva."""


class ReservaYaComenzo(ReservaRechazada):
    """RES-RF-06: la reserva ya comenzó; no se modifica ni se pregunta si mantenerla (E2)."""


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
    excluir_id=None,
) -> None:
    """Regla 3 (RES-RF-02): el estudiante no puede tener dos reservas que se crucen.

    ``excluir_id``: id de la reserva que se está modificando. Se ignora para
    que una reserva no choque consigo misma.
    """
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
        if excluir_id is not None and existente.pk == excluir_id:
            continue
        if candidata.solapa_estudiante(existente):
            raise ReservaRechazada(
                "El estudiante ya cuenta con un espacio reservado en ese horario."
            )


def _verificar_disponibilidad_sala(
    sala: Sala,
    fecha: datetime.date,
    hora_inicio: datetime.time,
    hora_fin: datetime.time,
    excluir_id=None,
) -> None:
    """Regla 4 (RES-RF-01, regla de oro): valida solapamientos con buffer de 15 minutos.

    ``excluir_id``: id de la reserva que se está modificando (no choca consigo misma).

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
        if excluir_id is not None and existente.pk == excluir_id:
            continue
        if candidata.choca_con(existente):
            raise ReservaRechazada(
                f"La sala '{sala.nombre}' no está disponible en ese horario "
                f"(se requieren {Reserva.BUFFER_MINUTOS} minutos de margen "
                f"entre reservas)."
            )


def _verificar_reserva_confirmada(reserva: Reserva) -> None:
    """Regla 5: solo se modifica una reserva confirmada (una cancelada no "revive")."""
    if reserva.estado != Reserva.ESTADO_CONFIRMADA:
        raise ReservaRechazada(
            "Solo se pueden modificar reservas confirmadas; esta está "
            f"{reserva.get_estado_display().lower()}."
        )


def inicio_de_reserva(reserva: Reserva) -> datetime.datetime:
    """Fecha y hora de inicio de la reserva, en la zona horaria del proyecto (America/La_Paz)."""
    return timezone.make_aware(
        datetime.datetime.combine(reserva.fecha, reserva.hora_inicio)
    )


def _verificar_no_ha_comenzado(reserva: Reserva, ahora: datetime.datetime) -> None:
    """Regla 6 (RES-RF-06, provisional): solo se modifica antes de que la reserva comience.

    "Ya comenzó" = el inicio es menor o igual que ``ahora``. Regla de la sesión 6;
    si el docente confirma la de la sesión 4 ("hasta 10 min después de crearla"),
    solo cambia esta función (usaría ``reserva.creado_en``).
    """
    if inicio_de_reserva(reserva) <= ahora:
        raise ReservaYaComenzo(
            "La reserva ya comenzó y no puede modificarse "
            f"(empezó el {reserva.fecha:%d/%m/%Y} a las {reserva.hora_inicio:%H:%M})."
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


def modificar_reserva_si_esta_disponible(
    *,
    reserva: Reserva,
    fecha: datetime.date,
    hora_inicio: datetime.time,
    hora_fin: datetime.time,
    ahora: Optional[datetime.datetime] = None,
) -> Reserva:
    """Cambia la fecha y el horario de una reserva solo si se cumplen todas las reglas.

    Sigue RES-CU-01 (sesión 7). La sala y el estudiante no cambian.

    Garantía (encargo, RES-RF-03): si alguna regla falla, la reserva original
    queda intacta en la base de datos; los valores nuevos solo se asignan
    después de que todas las reglas pasaron. Repetir la misma petición da el
    mismo resultado (la reserva no choca consigo misma).

    Parámetros:
        ahora: momento de referencia para RES-RF-06. Por defecto, la hora actual.
               Las pruebas lo fijan para no depender del reloj.

    Lanza:
        ReservaYaComenzo  si la reserva ya comenzó (E2: no se pregunta si mantenerla).
        ReservaRechazada  si otra regla falla (E1: se pregunta "¿Deseas mantenerla?").
        ValueError        si hora_fin <= hora_inicio.
    """
    if ahora is None:
        ahora = timezone.now()
    if hora_fin <= hora_inicio:
        raise ValueError("La hora de fin debe ser posterior a la hora de inicio.")

    _verificar_reserva_confirmada(reserva)
    _verificar_no_ha_comenzado(reserva, ahora)
    _verificar_estudiante_habilitado(reserva.estudiante)
    _verificar_sala_disponible(reserva.sala)
    _verificar_una_reserva_por_dia(
        reserva.estudiante, fecha, hora_inicio, hora_fin, excluir_id=reserva.pk
    )
    _verificar_disponibilidad_sala(
        reserva.sala, fecha, hora_inicio, hora_fin, excluir_id=reserva.pk
    )

    # Todas las reglas pasaron: recién ahora se cambian los datos.
    reserva.fecha = fecha
    reserva.hora_inicio = hora_inicio
    reserva.hora_fin = hora_fin
    reserva.save(update_fields=["fecha", "hora_inicio", "hora_fin"])
    return reserva
