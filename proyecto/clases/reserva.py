"""
proyecto/clases/reserva.py
==========================
Funciones simples y aisladas para la verificación de choques de horario,
consulta de disponibilidad y persistencia de reservas en MongoDB.
"""

from __future__ import annotations

import datetime
from typing import List, Optional, Tuple, Union

from ._db import asegurar_django
from .estudiante import obtener_estudiante, validar_estudiante_habilitado
from .horarios import (
    BUFFER_DESALOJO_MINUTOS,
    convertir_a_minutos,
    hay_choque_con_buffer,
    hay_solapamiento_simple,
    minutos_a_time,
    validar_rango_horario,
)
from .sala import obtener_sala, validar_sala_habilitada

asegurar_django()

from reservas.models import Estudiante as EstudianteModel
from reservas.models import Reserva as ReservaModel
from reservas.models import Sala as SalaModel


def normalizar_fecha(fecha: Optional[Union[str, datetime.date]]) -> datetime.date:
    """Convierte cadenas 'YYYY-MM-DD' o None a datetime.date (por defecto hoy)."""
    if fecha is None:
        return datetime.date.today()
    if isinstance(fecha, datetime.date):
        return fecha
    if isinstance(fecha, str):
        return datetime.datetime.strptime(fecha.strip(), "%Y-%m-%d").date()
    raise TypeError(f"Tipo de fecha no válido: {type(fecha)}. Use 'YYYY-MM-DD' o datetime.date.")


def revisar_choque_horario_dia(
    sala_ref: Union[str, int, SalaModel],
    fecha: Optional[Union[str, datetime.date]],
    hora_inicio: Union[str, datetime.time],
    hora_fin: Union[str, datetime.time],
    buffer_min: int = BUFFER_DESALOJO_MINUTOS,
) -> Tuple[bool, str]:
    """Función revisora: comprueba si un horario choca con alguna reserva existente en ese día.

    Aplica el margen obligatorio de desalojo (15 minutos por defecto).

    Retorna:
        Tuple[bool, str]:
            - bool: True si el horario está COMPLETAMENTE LIBRE, False si choca o la sala no existe.
            - str: Mensaje descriptivo con el detalle del choque o confirmación.
    """
    sala = sala_ref if isinstance(sala_ref, SalaModel) else obtener_sala(sala_ref)
    if sala is None:
        return False, f"La sala '{sala_ref}' no existe."

    fecha_obj = normalizar_fecha(fecha)
    min_ini, min_fin = validar_rango_horario(hora_inicio, hora_fin)

    reservas_del_dia = ReservaModel.objects.filter(
        sala=sala,
        fecha=fecha_obj,
        estado=ReservaModel.ESTADO_CONFIRMADA,
    )

    for r in reservas_del_dia:
        r_ini = convertir_a_minutos(r.hora_inicio)
        r_fin = convertir_a_minutos(r.hora_fin)
        if hay_choque_con_buffer(min_ini, min_fin, r_ini, r_fin, buffer_min):
            return (
                False,
                f"Cruce de horarios o no se respetan los {buffer_min} minutos de desalojo "
                f"con reserva existente ({r.hora_inicio:%H:%M}-{r.hora_fin:%H:%M}).",
            )

    return True, f"Horario libre para la sala '{sala.nombre}' en fecha {fecha_obj}."


def revisar_reserva_estudiante_en_horario(
    estudiante_ref: Union[str, int, EstudianteModel],
    fecha: Optional[Union[str, datetime.date]],
    hora_inicio: Union[str, datetime.time],
    hora_fin: Union[str, datetime.time],
) -> Tuple[bool, str]:
    """Comprueba si el estudiante ya cuenta con otra reserva activa en ese mismo bloque horario.

    Retorna:
        Tuple[bool, str]:
            - bool: True si no tiene solapamientos, False si ya tiene reserva simultánea.
            - str: Mensaje descriptivo.
    """
    estudiante = (
        estudiante_ref
        if isinstance(estudiante_ref, EstudianteModel)
        else obtener_estudiante(estudiante_ref)
    )
    if estudiante is None:
        return False, f"Estudiante '{estudiante_ref}' no encontrado."

    fecha_obj = normalizar_fecha(fecha)
    min_ini, min_fin = validar_rango_horario(hora_inicio, hora_fin)

    reservas_estudiante = ReservaModel.objects.filter(
        estudiante=estudiante,
        fecha=fecha_obj,
        estado=ReservaModel.ESTADO_CONFIRMADA,
    )

    for r in reservas_estudiante:
        r_ini = convertir_a_minutos(r.hora_inicio)
        r_fin = convertir_a_minutos(r.hora_fin)
        if hay_solapamiento_simple(min_ini, min_fin, r_ini, r_fin):
            return (
                False,
                f"El estudiante ya cuenta con un espacio reservado en ese horario ({r.sala.nombre} {r.hora_inicio:%H:%M}-{r.hora_fin:%H:%M}).",
            )

    return True, "El estudiante no tiene otras reservas en ese horario."


def guardar_reserva_mongo(
    estudiante: EstudianteModel,
    sala: SalaModel,
    fecha: datetime.date,
    hora_inicio: Union[str, datetime.time],
    hora_fin: Union[str, datetime.time],
) -> ReservaModel:
    """Inserta directamente un registro de reserva confirmada en la base de datos de MongoDB."""
    h_ini_obj = (
        minutos_a_time(convertir_a_minutos(hora_inicio))
        if not isinstance(hora_inicio, datetime.time)
        else hora_inicio
    )
    h_fin_obj = (
        minutos_a_time(convertir_a_minutos(hora_fin))
        if not isinstance(hora_fin, datetime.time)
        else hora_fin
    )

    reserva = ReservaModel.objects.create(
        estudiante=estudiante,
        sala=sala,
        fecha=fecha,
        hora_inicio=h_ini_obj,
        hora_fin=h_fin_obj,
        estado=ReservaModel.ESTADO_CONFIRMADA,
    )
    return reserva


def cancelar_reserva_en_mongo(
    codigo_estudiante: Union[str, int],
    nombre_o_id_sala: Union[str, int],
    fecha: Optional[Union[str, datetime.date]] = None,
) -> Tuple[bool, str]:
    """Cancela una reserva activa de un estudiante en MongoDB.

    Retorna:
        Tuple[bool, str]: (exito, mensaje)
    """
    estudiante = obtener_estudiante(codigo_estudiante)
    sala = obtener_sala(nombre_o_id_sala)

    if not estudiante or not sala:
        return False, "No se encontró ninguna reserva activa."

    query = {
        "estudiante": estudiante,
        "sala": sala,
        "estado": ReservaModel.ESTADO_CONFIRMADA,
    }
    if fecha:
        query["fecha"] = normalizar_fecha(fecha)

    reserva = ReservaModel.objects.filter(**query).first()
    if not reserva:
        return False, "No se encontró ninguna reserva activa."

    reserva.estado = ReservaModel.ESTADO_CANCELADA
    reserva.save()
    return True, "Reserva cancelada correctamente."


def consultar_salas_disponibles_dia(
    fecha: Optional[Union[str, datetime.date]],
    hora_inicio: Union[str, datetime.time],
    hora_fin: Union[str, datetime.time],
    buffer_min: int = BUFFER_DESALOJO_MINUTOS,
) -> List[str]:
    """Retorna los nombres de las salas que se encuentran disponibles para un bloque horario."""
    fecha_obj = normalizar_fecha(fecha)
    salas = SalaModel.objects.filter(en_mantenimiento=False)
    disponibles = []

    for sala in salas:
        libre, _ = revisar_choque_horario_dia(sala, fecha_obj, hora_inicio, hora_fin, buffer_min)
        if libre:
            disponibles.append(sala.nombre)

    return disponibles


class Reserva:
    """Clase liviana de Reserva para compatibilidad."""

    def __init__(self, sala, estudiante, hora_inicio, hora_fin, fecha=None):
        self.sala = sala
        self.estudiante = estudiante
        self.hora_inicio = str(hora_inicio)
        self.hora_fin = str(hora_fin)
        self.fecha = normalizar_fecha(fecha)
        self.min_inicio = convertir_a_minutos(hora_inicio)
        self.min_fin = convertir_a_minutos(hora_fin)

    def choca_con(self, otra_reserva, buffer_min: int = 15) -> bool:
        sala_id_self = getattr(self.sala, "id", str(self.sala))
        sala_id_otra = getattr(otra_reserva.sala, "id", str(otra_reserva.sala))
        if sala_id_self != sala_id_otra:
            return False
        return hay_choque_con_buffer(
            self.min_inicio, self.min_fin, otra_reserva.min_inicio, otra_reserva.min_fin, buffer_min
        )

    def es_del_mismo_estudiante_en_bloque(self, otra_reserva) -> bool:
        cod_self = getattr(self.estudiante, "codigo", str(self.estudiante))
        cod_otra = getattr(otra_reserva.estudiante, "codigo", str(otra_reserva.estudiante))
        if cod_self != cod_otra:
            return False
        return hay_solapamiento_simple(
            self.min_inicio, self.min_fin, otra_reserva.min_inicio, otra_reserva.min_fin
        )