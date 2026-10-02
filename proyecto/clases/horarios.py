"""
proyecto/clases/horarios.py
===========================
Funciones simples y aisladas para el manejo, conversión y validación de horarios
y cálculo de colisiones de tiempo con margen de seguridad (buffer de 15 minutos).
"""

from __future__ import annotations

import datetime
from typing import Union

BUFFER_DESALOJO_MINUTOS = 15


def convertir_a_minutos(hora: Union[str, datetime.time]) -> int:
    """Convierte una hora en formato 'HH:MM' o datetime.time a minutos desde medianoche.

    Ejemplos:
        '10:00' -> 600
        '07:45' -> 465
        datetime.time(12, 30) -> 750
    """
    if isinstance(hora, datetime.time):
        return hora.hour * 60 + hora.minute

    if not isinstance(hora, str):
        raise TypeError(f"Formato de hora no soportado: {type(hora)}. Use 'HH:MM' o datetime.time.")

    partes = hora.strip().split(":")
    if len(partes) != 2:
        raise ValueError(f"Formato de hora inválido: '{hora}'. Debe ser 'HH:MM'.")

    try:
        horas = int(partes[0])
        minutos = int(partes[1])
    except ValueError:
        raise ValueError(f"Valores numéricos inválidos en hora: '{hora}'.")

    if not (0 <= horas <= 23 and 0 <= minutos <= 59):
        raise ValueError(f"Hora fuera de rango válido (00:00 - 23:59): '{hora}'.")

    return horas * 60 + minutos


def minutos_a_time(minutos: int) -> datetime.time:
    """Convierte minutos desde medianoche a un objeto datetime.time."""
    if not (0 <= minutos < 1440):
        raise ValueError(f"Minutos fuera de rango diario (0 - 1439): {minutos}")
    return datetime.time(hour=minutos // 60, minute=minutos % 60)


def validar_rango_horario(
    hora_inicio: Union[str, datetime.time],
    hora_fin: Union[str, datetime.time],
) -> tuple[int, int]:
    """Valida que la hora de fin sea estrictamente posterior a la hora de inicio.

    Retorna:
        tuple[int, int]: (minutos_inicio, minutos_fin)
    """
    min_inicio = convertir_a_minutos(hora_inicio)
    min_fin = convertir_a_minutos(hora_fin)

    if min_fin <= min_inicio:
        raise ValueError(
            f"La hora de fin ({hora_fin}) debe ser posterior a la hora de inicio ({hora_inicio})."
        )

    return min_inicio, min_fin


def hay_choque_con_buffer(
    inicio_a: Union[int, str, datetime.time],
    fin_a: Union[int, str, datetime.time],
    inicio_b: Union[int, str, datetime.time],
    fin_b: Union[int, str, datetime.time],
    buffer_min: int = BUFFER_DESALOJO_MINUTOS,
) -> bool:
    """Verifica si dos intervalos de tiempo chocan considerando el buffer de desalojo.

    Regla: Para la misma sala, se requiere un margen de buffer_min (15 min) entre reservas.
    Dos reservas [inicio_a, fin_a] e [inicio_b, fin_b] chocan si:
    inicio_a < (fin_b + buffer_min) and fin_a > (inicio_b - buffer_min)
    """
    min_inicio_a = convertir_a_minutos(inicio_a) if not isinstance(inicio_a, int) else inicio_a
    min_fin_a = convertir_a_minutos(fin_a) if not isinstance(fin_a, int) else fin_a
    min_inicio_b = convertir_a_minutos(inicio_b) if not isinstance(inicio_b, int) else inicio_b
    min_fin_b = convertir_a_minutos(fin_b) if not isinstance(fin_b, int) else fin_b

    return min_inicio_a < (min_fin_b + buffer_min) and min_fin_a > (min_inicio_b - buffer_min)


def hay_solapamiento_simple(
    inicio_a: Union[int, str, datetime.time],
    fin_a: Union[int, str, datetime.time],
    inicio_b: Union[int, str, datetime.time],
    fin_b: Union[int, str, datetime.time],
) -> bool:
    """Verifica si dos intervalos de tiempo se cruzan directamente (sin buffer).

    Se utiliza para verificar si un mismo estudiante intenta estar en dos salas al mismo tiempo.
    """
    min_inicio_a = convertir_a_minutos(inicio_a) if not isinstance(inicio_a, int) else inicio_a
    min_fin_a = convertir_a_minutos(fin_a) if not isinstance(fin_a, int) else fin_a
    min_inicio_b = convertir_a_minutos(inicio_b) if not isinstance(inicio_b, int) else inicio_b
    min_fin_b = convertir_a_minutos(fin_b) if not isinstance(fin_b, int) else fin_b

    return min_inicio_a < min_fin_b and min_fin_a > min_inicio_b


def parsear_horas(horas: Union[tuple, list, str]) -> tuple[datetime.time, datetime.time]:
    """Parsea diferentes formatos de entrada de horas a objetos datetime.time.

    Formatos aceptados:
        - ("10:00", "12:00")
        - ["10:00", "12:00"]
        - "10:00-12:00" o "10:00 - 12:00"
        - (datetime.time(10, 0), datetime.time(12, 0))
    """
    if isinstance(horas, str):
        partes = [p.strip() for p in horas.split("-")]
        if len(partes) != 2:
            raise ValueError(f"Cadena de horas inválida: '{horas}'. Use formato 'HH:MM-HH:MM'.")
        h_inicio, h_fin = partes[0], partes[1]
    elif isinstance(horas, (tuple, list)) and len(horas) == 2:
        h_inicio, h_fin = horas[0], horas[1]
    else:
        raise ValueError(f"Parámetro de horas inválido: {horas}. Debe ser una tupla o cadena 'HH:MM-HH:MM'.")

    min_ini, min_fin = validar_rango_horario(h_inicio, h_fin)
    return minutos_a_time(min_ini), minutos_a_time(min_fin)
