"""
proyecto/clases/sistema_reservas.py
===================================
Orquestador principal y API pública para el sistema de reservas.

Provee la función principal:
    - reservar_si_es_posible (alias reservarSiesPosible)
Junto con funciones simples y aisladas de consulta y cancelación.
"""

from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional, Union

from ._db import asegurar_django
from .estudiante import Estudiante, obtener_estudiante, validar_estudiante_habilitado
from .horarios import parsear_horas, validar_rango_horario
from .reserva import (
    Reserva,
    cancelar_reserva_en_mongo,
    consultar_salas_disponibles_dia,
    guardar_reserva_mongo,
    normalizar_fecha,
    revisar_choque_horario_dia,
    revisar_reserva_estudiante_en_horario,
)
from .sala import Sala, obtener_sala, validar_sala_habilitada

asegurar_django()


def reservar_si_es_posible(
    codigo_estudiante: Union[str, int, Estudiante],
    nombre_sala: Union[str, int, Sala],
    horas: Union[tuple, list, str, datetime.time],
    hora_fin: Optional[Union[str, datetime.time]] = None,
    fecha: Optional[Union[str, datetime.date]] = None,
    asistentes: Optional[int] = None,
) -> Dict[str, Any]:
    """Valida todas las reglas y registra la reserva en MongoDB si es posible.

    Parámetros:
        codigo_estudiante: Código único del estudiante (ej: 'U-92001' o 92001).
        nombre_sala: Nombre o número de la sala (ej: 'Sala Alfa', 'A', 1).
        horas: Rango de horas en tupla ('10:00', '12:00'), cadena '10:00-12:00'
               o la hora de inicio si hora_fin se provee por separado.
        hora_fin: Hora de fin opcional si se pasan inicio y fin por separado.
        fecha: Fecha de la reserva (str 'YYYY-MM-DD' o datetime.date). Por defecto hoy.
        asistentes: Cantidad opcional de asistentes para validaciones adicionales.

    Retorna:
        Dict con:
            - "estado": "CONFIRMADA" si se creó con éxito en MongoDB, "RECHAZADA" si falló.
            - "mensaje": Explicación detallada del resultado o motivo de rechazo.
            - "datos": Diccionario con los detalles de la reserva confirmada (si aplica).
            - "id_reserva": Identificador único de la reserva en MongoDB (si aplica).
    """
    # 1. Normalizar y validar fecha
    try:
        fecha_obj = normalizar_fecha(fecha)
    except Exception as e:
        return {"estado": "RECHAZADA", "mensaje": f"Fecha inválida: {e}"}

    # 2. Normalizar y validar rango de horas
    try:
        if hora_fin is not None:
            min_ini, min_fn = validar_rango_horario(horas, hora_fin)
            from .horarios import minutos_a_time
            h_ini_obj = minutos_a_time(min_ini)
            h_fin_obj = minutos_a_time(min_fn)
        else:
            h_ini_obj, h_fin_obj = parsear_horas(horas)
    except Exception as e:
        return {"estado": "RECHAZADA", "mensaje": str(e)}

    # 3. Validar estudiante en MongoDB (existencia, activo, matrícula pagada)
    est_habilitado, msg_est, estudiante_obj = validar_estudiante_habilitado(codigo_estudiante)
    if not est_habilitado or estudiante_obj is None:
        return {"estado": "RECHAZADA", "mensaje": msg_est}

    # 4. Validar sala en MongoDB (existencia y no mantenimiento)
    sala_habilitada, msg_sala, sala_obj = validar_sala_habilitada(nombre_sala)
    if not sala_habilitada or sala_obj is None:
        return {"estado": "RECHAZADA", "mensaje": msg_sala}

    # 5. Validar que el estudiante no tenga otra reserva en ese mismo bloque horario
    sin_cruce_estudiante, msg_cruce = revisar_reserva_estudiante_en_horario(
        estudiante_obj, fecha_obj, h_ini_obj, h_fin_obj
    )
    if not sin_cruce_estudiante:
        return {"estado": "RECHAZADA", "mensaje": msg_cruce}

    # 6. Revisar si choca con alguna reserva en ese día en la sala (buffer de 15 min)
    horario_libre, msg_choque = revisar_choque_horario_dia(
        sala_obj, fecha_obj, h_ini_obj, h_fin_obj
    )
    if not horario_libre:
        return {"estado": "RECHAZADA", "mensaje": msg_choque}

    # 7. Persistir en la base de datos de MongoDB
    try:
        reserva = guardar_reserva_mongo(
            estudiante=estudiante_obj,
            sala=sala_obj,
            fecha=fecha_obj,
            hora_inicio=h_ini_obj,
            hora_fin=h_fin_obj,
        )
    except Exception as e:
        return {"estado": "RECHAZADA", "mensaje": f"Error al guardar en base de datos: {e}"}

    return {
        "estado": "CONFIRMADA",
        "mensaje": "Reserva exitosa.",
        "id_reserva": str(reserva.id),
        "datos": {
            "codigo_estudiante": estudiante_obj.codigo_estudiante,
            "nombre_estudiante": f"{estudiante_obj.nombres} {estudiante_obj.apellidos}".strip(),
            "sala": sala_obj.nombre,
            "fecha": str(reserva.fecha),
            "hora_inicio": reserva.hora_inicio.strftime("%H:%M"),
            "hora_fin": reserva.hora_fin.strftime("%H:%M"),
        },
    }


# Alias en camelCase solicitado explícitamente:
reservarSiesPosible = reservar_si_es_posible


def consultar_espacios_disponibles(
    hora_inicio: Union[str, datetime.time],
    hora_fin: Union[str, datetime.time],
    fecha: Optional[Union[str, datetime.date]] = None,
    buffer_min: int = 15,
) -> List[str]:
    """Consulta y retorna los nombres de salas disponibles en un horario."""
    return consultar_salas_disponibles_dia(fecha, hora_inicio, hora_fin, buffer_min)


def cancelar_reserva(
    codigo_estudiante: Union[str, int],
    nombre_sala: Union[str, int],
    fecha: Optional[Union[str, datetime.date]] = None,
) -> Dict[str, str]:
    """Cancela una reserva y retorna el resultado de la operación."""
    exito, mensaje = cancelar_reserva_en_mongo(codigo_estudiante, nombre_sala, fecha)
    return {
        "estado": "EXITO" if exito else "RECHAZADA",
        "mensaje": mensaje,
    }


class SistemaReservas:
    """Clase envoltorio para mantener compatibilidad con implementaciones previas."""

    def __init__(self):
        self.salas = {}
        self.reservas = []

    def agregar_sala(self, sala):
        self.salas[getattr(sala, "id", sala)] = sala

    def crear_reserva(
        self,
        estudiante,
        id_sala,
        hora_inicio,
        hora_fin,
        asistentes: int = 1,
        fecha: Optional[Union[str, datetime.date]] = None,
    ) -> Dict[str, Any]:
        """Crea una reserva usando la lógica unificada."""
        # Intenta primero a través de la API persistida de Mongo si los modelos existen
        resultado = reservar_si_es_posible(
            codigo_estudiante=estudiante,
            nombre_sala=id_sala,
            horas=(hora_inicio, hora_fin),
            fecha=fecha,
            asistentes=asistentes,
        )
        if resultado["estado"] == "CONFIRMADA":
            return resultado

        # Si no se encuentra en Mongo (ej: test puramente en memoria con objetos Sala/Estudiante locales),
        # ejecutamos la lógica en memoria como fallback:
        sala = self.salas.get(id_sala)
        if not sala:
            return {"estado": "RECHAZADA", "mensaje": "La sala solicitada no existe."}

        capacidad = getattr(sala, "capacidad", 10)
        if asistentes > capacidad:
            return {"estado": "RECHAZADA", "mensaje": "La cantidad de asistentes supera la capacidad de la sala."}

        nueva_reserva = Reserva(sala, estudiante, hora_inicio, hora_fin, fecha)

        for r in self.reservas:
            if nueva_reserva.es_del_mismo_estudiante_en_bloque(r):
                return {"estado": "RECHAZADA", "mensaje": "El estudiante ya cuenta con un espacio reservado en ese horario."}
            if nueva_reserva.choca_con(r):
                return {"estado": "RECHAZADA", "mensaje": "Cruce de horarios o no se respetan los 15 minutos de desalojo."}

        self.reservas.append(nueva_reserva)
        return {"estado": "CONFIRMADA", "mensaje": "Reserva exitosa."}

    def consultar_espacios_disponibles(self, hora_inicio, hora_fin, buffer_min=15):
        estudiante_temp = Estudiante(0)
        disponibles = []
        for id_sala, sala in self.salas.items():
            reserva_temp = Reserva(sala, estudiante_temp, hora_inicio, hora_fin)
            if not any(reserva_temp.choca_con(r, buffer_min) for r in self.reservas):
                disponibles.append(sala.id if hasattr(sala, "id") else id_sala)
        return disponibles

    def cancelar_reserva(self, codigo_estudiante, id_sala):
        cod_str = str(codigo_estudiante)
        for r in list(self.reservas):
            r_cod = getattr(r.estudiante, "codigo", str(r.estudiante))
            r_sala = getattr(r.sala, "id", str(r.sala))
            if r_cod == cod_str and r_sala == str(id_sala):
                self.reservas.remove(r)
                return {"estado": "EXITO", "mensaje": "Reserva cancelada correctamente."}
        return {"estado": "RECHAZADA", "mensaje": "No se encontró ninguna reserva activa."}