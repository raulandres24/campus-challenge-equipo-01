"""
reservas/ventanas.py
====================
Desde cuándo puede reservar cada nivel (regla de anticipación). Funciones puras: no usan
la base de datos, por eso se prueban sin MongoDB.

Reglas del docente (07/10/2026), con los días de clase de lunes a viernes:

- **Postgrado y doctorado:** reservan hasta **2 días de clase** adelante, sin importar la
  hora. Desde el lunes (a cualquier hora) hasta el miércoles todo el día; el viernes, hasta
  el martes. Sábado y domingo no hay clases, así que no cuentan como días de clase.
- **Pregrado:** las reservas de un día se abren a las **18:00 del día de clase anterior**:
  el lunes a las 18:00 ya pueden reservar el martes, a cualquier hora.

Interpretaciones (pendientes de confirmar, ver README, preguntas P9, P10 y P12):
- Se cuenta desde hoy: se puede reservar para hoy y para los días siguientes hasta el límite.
- El viernes a las 18:00 pregrado abre el lunes (el «día siguiente» con clases).
- Los sábados y domingos no se bloquean; solo siguen la misma regla de apertura.
- Los administradores y el docente no están sujetos a estas reglas (lo decide la vista).
"""

from __future__ import annotations

import datetime
from typing import Optional
from zoneinfo import ZoneInfo

ZONA_LOCAL = ZoneInfo("America/La_Paz")

POSGRADO_DIAS_DE_CLASE_ADELANTE = 2
PREGRADO_HORA_DE_APERTURA = datetime.time(18, 0)
NIVELES_POSGRADO = frozenset({"postgrado", "doctorado"})

_DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


def es_dia_de_clase(fecha: datetime.date) -> bool:
    """Lunes a viernes."""
    return fecha.weekday() < 5


def dia_de_clase_anterior(fecha: datetime.date, cuantos: int) -> datetime.date:
    """El día de clase que está ``cuantos`` días de clase antes de ``fecha`` (sin contar ``fecha``)."""
    dia, contados = fecha, 0
    while contados < cuantos:
        dia -= datetime.timedelta(days=1)
        if es_dia_de_clase(dia):
            contados += 1
    return dia


def apertura_de_reservas(nivel: str, fecha: datetime.date) -> datetime.datetime:
    """Momento (hora local, sin zona) desde el cual ese nivel puede reservar para ``fecha``."""
    if (nivel or "").strip().lower() in NIVELES_POSGRADO:
        dia = dia_de_clase_anterior(fecha, POSGRADO_DIAS_DE_CLASE_ADELANTE)
        return datetime.datetime.combine(dia, datetime.time(0, 0))
    dia = dia_de_clase_anterior(fecha, 1)
    return datetime.datetime.combine(dia, PREGRADO_HORA_DE_APERTURA)


def _a_hora_local(ahora: datetime.datetime) -> datetime.datetime:
    """Pasa ``ahora`` a la hora de La Paz y le quita la zona, para compararla con la apertura."""
    if ahora.tzinfo is not None:
        ahora = ahora.astimezone(ZONA_LOCAL).replace(tzinfo=None)
    return ahora


def puede_reservar_para(nivel: str, fecha: datetime.date, ahora: datetime.datetime) -> bool:
    """True si, a la hora ``ahora``, ese nivel ya puede reservar para ``fecha``."""
    return _a_hora_local(ahora) >= apertura_de_reservas(nivel, fecha)


def ultima_fecha_reservable(nivel: str, ahora: datetime.datetime) -> datetime.date:
    """Último día para el que ese nivel puede reservar a la hora ``ahora``."""
    hoy = _a_hora_local(ahora).date()
    ultima = hoy
    for adelante in range(0, 15):
        dia = hoy + datetime.timedelta(days=adelante)
        if puede_reservar_para(nivel, dia, ahora):
            ultima = dia
    return ultima


def _texto_fecha(fecha: datetime.date) -> str:
    return f"{_DIAS[fecha.weekday()]} {fecha:%d/%m/%Y}"


def mensaje_fuera_de_ventana(nivel: str, fecha: datetime.date) -> str:
    """Explica por qué todavía no se puede reservar para ``fecha`` y cuándo se abre."""
    apertura = apertura_de_reservas(nivel, fecha)
    if (nivel or "").strip().lower() in NIVELES_POSGRADO:
        desde = f"el {_texto_fecha(apertura.date())}"
    else:
        desde = f"el {_texto_fecha(apertura.date())} a las {apertura:%H:%M}"
    return f"Aún no puedes reservar para el {_texto_fecha(fecha)}. Las reservas para ese día se abren {desde}."
