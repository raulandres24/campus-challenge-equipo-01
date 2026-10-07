"""
tests/test_integracion_completa.py
==================================
Suite de 10 Pruebas de Integración Multi-función.
Cada prueba combina múltiples funciones del sistema para verificar flujos
completos de negocio, validaciones cruzadas y persistencia real en MongoDB.
"""

import datetime
import pytest

from proyecto.clases import (
    cancelar_reserva,
    consultar_espacios_disponibles,
    reservar_si_es_posible,
)
from reservas.models import Estudiante, Reserva, Sala

# Este módulo usa MongoDB: corre sobre la base de pruebas (test_...), nunca sobre la real.
pytestmark = pytest.mark.usefixtures("limpiar_reservas_test")


# ==============================================================================
# 10 Pruebas de Integración Multi-función (Validación en MongoDB)
# ==============================================================================

def test_01_flujo_completo_reserva_exitosa_y_verificacion_datos_mongo(
    estudiante_habilitado_db, sala_disponible_db
):
    """Integración 1: Flujo completo de reserva exitosa con verificación directa en MongoDB.

    Combina: normalización de fecha, parseo de horas, validación de estudiante,
    validación de sala, revisión de choque con buffer y persistencia en MongoDB.
    """
    hoy = datetime.date.today()
    resultado = reservar_si_es_posible(
        codigo_estudiante=estudiante_habilitado_db.codigo_estudiante,
        nombre_sala=sala_disponible_db.nombre,
        horas=("10:00", "12:00"),
        fecha=hoy,
    )

    # 1. Validación de respuesta de la función orquestadora
    assert resultado["estado"] == "CONFIRMADA"
    assert resultado["mensaje"] == "Reserva exitosa."
    assert "id_reserva" in resultado

    # 2. Validación de datos directamente en la base de datos de MongoDB
    reserva_db = Reserva.objects.get(id=resultado["id_reserva"])
    assert reserva_db.estudiante_id == estudiante_habilitado_db.id
    assert reserva_db.sala_id == sala_disponible_db.id
    assert reserva_db.fecha == hoy
    assert reserva_db.hora_inicio == datetime.time(10, 0)
    assert reserva_db.hora_fin == datetime.time(12, 0)
    assert reserva_db.estado == Reserva.ESTADO_CONFIRMADA


def test_02_rechazo_reserva_estudiante_inactivo_sin_guardar_mongo(
    estudiante_inactivo_db, sala_disponible_db
):
    """Integración 2: Rechazo de reserva por estudiante inactivo y comprobación de cero registros en Mongo.

    Combina: validación de estudiante en MongoDB con interrupción temprana del flujo.
    """
    hoy = datetime.date.today()
    resultado = reservar_si_es_posible(
        codigo_estudiante=estudiante_inactivo_db.codigo_estudiante,
        nombre_sala=sala_disponible_db.nombre,
        horas=("10:00", "12:00"),
        fecha=hoy,
    )

    assert resultado["estado"] == "RECHAZADA"
    assert "no está activo" in resultado["mensaje"]

    # Validar que NO se insertó ningún documento en MongoDB para este estudiante
    conteo_mongo = Reserva.objects.filter(estudiante_id=estudiante_inactivo_db.id).count()
    assert conteo_mongo == 0


def test_03_rechazo_reserva_estudiante_sin_matricula_pagada(
    estudiante_sin_matricula_db, sala_disponible_db
):
    """Integración 3: Rechazo de reserva por matrícula pendiente y comprobación de no persistencia en Mongo.

    Combina: verificación de estado financiero del estudiante en Mongo antes de reservar.
    """
    hoy = datetime.date.today()
    resultado = reservar_si_es_posible(
        codigo_estudiante=estudiante_sin_matricula_db.codigo_estudiante,
        nombre_sala=sala_disponible_db.nombre,
        horas=("14:00", "16:00"),
        fecha=hoy,
    )

    assert resultado["estado"] == "RECHAZADA"
    assert "no tiene la matrícula pagada" in resultado["mensaje"]

    # Comprobación de no persistencia en MongoDB
    conteo_mongo = Reserva.objects.filter(estudiante_id=estudiante_sin_matricula_db.id).count()
    assert conteo_mongo == 0


def test_04_rechazo_reserva_sala_en_mantenimiento(
    estudiante_habilitado_db, sala_mantenimiento_db
):
    """Integración 4: Rechazo cuando la sala solicitada está en mantenimiento técnico.

    Combina: validación de estado operativo de sala en MongoDB y rechazo de reserva.
    """
    hoy = datetime.date.today()
    resultado = reservar_si_es_posible(
        codigo_estudiante=estudiante_habilitado_db.codigo_estudiante,
        nombre_sala=sala_mantenimiento_db.nombre,
        horas=("09:00", "11:00"),
        fecha=hoy,
    )

    assert resultado["estado"] == "RECHAZADA"
    assert "en mantenimiento" in resultado["mensaje"]

    # Comprobación de no persistencia en MongoDB
    conteo_mongo = Reserva.objects.filter(sala_id=sala_mantenimiento_db.id).count()
    assert conteo_mongo == 0


def test_05_rechazo_reserva_sala_inexistente(estudiante_habilitado_db):
    """Integración 5: Rechazo cuando se solicita una sala que no existe en MongoDB.

    Combina: consulta de catálogo de salas en MongoDB con reporte de error descriptivo.
    """
    hoy = datetime.date.today()
    resultado = reservar_si_es_posible(
        codigo_estudiante=estudiante_habilitado_db.codigo_estudiante,
        nombre_sala="Sala 999 Fantasma",
        horas=("10:00", "12:00"),
        fecha=hoy,
    )

    assert resultado["estado"] == "RECHAZADA"
    assert "no existe" in resultado["mensaje"]


def test_06_rechazo_choque_exacto_de_horario_misma_sala(
    estudiante_habilitado_db, sala_disponible_db
):
    """Integración 6: Rechazo por cruce directo de horario en la misma sala y fecha.

    Combina: creación de primera reserva en Mongo + intento de solapamiento total por otro estudiante.
    """
    hoy = datetime.date.today()
    # 1. Crear segundo estudiante habilitado
    estudiante_dos, _ = Estudiante.objects.get_or_create(
        codigo_estudiante="TEST-E04",
        defaults={
            "nombres": "Estudiante",
            "apellidos": "Dos",
            "esta_activo": True,
            "matricula_pagada": True,
        },
    )

    # 2. Primera reserva: 08:00 - 10:00 (Exitosa)
    res_1 = reservar_si_es_posible(
        codigo_estudiante=estudiante_habilitado_db.codigo_estudiante,
        nombre_sala=sala_disponible_db.nombre,
        horas=("08:00", "10:00"),
        fecha=hoy,
    )
    assert res_1["estado"] == "CONFIRMADA"

    # 3. Segunda reserva por otro estudiante en el mismo bloque: 08:00 - 10:00 (Rechazada)
    res_2 = reservar_si_es_posible(
        codigo_estudiante=estudiante_dos.codigo_estudiante,
        nombre_sala=sala_disponible_db.nombre,
        horas=("08:00", "10:00"),
        fecha=hoy,
    )
    assert res_2["estado"] == "RECHAZADA"
    assert "Cruce de horarios" in res_2["mensaje"]

    # Validar en Mongo que solo existe la primera reserva confirmada
    reservas_mongo = Reserva.objects.filter(sala_id=sala_disponible_db.id, fecha=hoy)
    assert reservas_mongo.count() == 1
    assert reservas_mongo.first().estudiante_id == estudiante_habilitado_db.id


def test_07_rechazo_violacion_buffer_15_minutos_desalojo(
    estudiante_habilitado_db, sala_disponible_db
):
    """Integración 7: Rechazo por violación del margen de 15 minutos de desalojo/limpieza.

    Combina: reserva previa (08:00 a 10:00) con intento a las 10:10 (solo 10 min de margen < 15 min buffer).
    """
    hoy = datetime.date.today()
    estudiante_dos, _ = Estudiante.objects.get_or_create(
        codigo_estudiante="TEST-E05",
        defaults={
            "nombres": "Estudiante",
            "apellidos": "Cinco",
            "esta_activo": True,
            "matricula_pagada": True,
        },
    )

    # Reserva 1: 08:00 a 10:00
    res_1 = reservar_si_es_posible(
        codigo_estudiante=estudiante_habilitado_db.codigo_estudiante,
        nombre_sala=sala_disponible_db.nombre,
        horas=("08:00", "10:00"),
        fecha=hoy,
    )
    assert res_1["estado"] == "CONFIRMADA"

    # Reserva 2: 10:10 a 12:00 (Debe fallar porque 10:10 - 10:00 = 10 min < 15 min buffer)
    res_2 = reservar_si_es_posible(
        codigo_estudiante=estudiante_dos.codigo_estudiante,
        nombre_sala=sala_disponible_db.nombre,
        horas=("10:10", "12:00"),
        fecha=hoy,
    )
    assert res_2["estado"] == "RECHAZADA"
    assert "15 minutos de desalojo" in res_2["mensaje"]


def test_08_aceptacion_limite_exacto_buffer_15_minutos(
    estudiante_habilitado_db, sala_disponible_db
):
    """Integración 8: Aceptación en el límite exacto del intervalo de 15 minutos de buffer.

    Combina: reserva 1 (08:00 a 10:00) con reserva 2 (10:15 a 12:00 -> exactamente 15 min de margen).
    """
    hoy = datetime.date.today()
    estudiante_dos, _ = Estudiante.objects.get_or_create(
        codigo_estudiante="TEST-E06",
        defaults={
            "nombres": "Estudiante",
            "apellidos": "Seis",
            "esta_activo": True,
            "matricula_pagada": True,
        },
    )

    # Reserva 1: 08:00 a 10:00
    res_1 = reservar_si_es_posible(
        codigo_estudiante=estudiante_habilitado_db.codigo_estudiante,
        nombre_sala=sala_disponible_db.nombre,
        horas=("08:00", "10:00"),
        fecha=hoy,
    )
    assert res_1["estado"] == "CONFIRMADA"

    # Reserva 2: 10:15 a 12:00 (Debe ser confirmada porque respeta exactamente los 15 minutos)
    res_2 = reservar_si_es_posible(
        codigo_estudiante=estudiante_dos.codigo_estudiante,
        nombre_sala=sala_disponible_db.nombre,
        horas=("10:15", "12:00"),
        fecha=hoy,
    )
    assert res_2["estado"] == "CONFIRMADA"

    # Validar que AMBAS reservas quedaron guardadas en MongoDB
    conteo_mongo = Reserva.objects.filter(sala_id=sala_disponible_db.id, fecha=hoy).count()
    assert conteo_mongo == 2


def test_09_rechazo_estudiante_con_doble_reserva_en_mismo_horario(
    estudiante_habilitado_db, sala_disponible_db
):
    """Integración 9: Rechazo si el mismo estudiante intenta reservar dos salas diferentes en el mismo bloque.

    Combina: validación de historial de reservas del solicitante en MongoDB a través de múltiples salas.
    """
    hoy = datetime.date.today()
    # Crear segunda sala disponible
    sala_beta, _ = Sala.objects.get_or_create(
        nombre="Test Sala Beta",
        defaults={"en_mantenimiento": False},
    )
    sala_beta.en_mantenimiento = False
    sala_beta.save()

    # 1. Estudiante reserva Sala Alfa de 14:00 a 16:00
    res_1 = reservar_si_es_posible(
        codigo_estudiante=estudiante_habilitado_db.codigo_estudiante,
        nombre_sala=sala_disponible_db.nombre,
        horas=("14:00", "16:00"),
        fecha=hoy,
    )
    assert res_1["estado"] == "CONFIRMADA"

    # 2. Mismo estudiante intenta reservar Sala Beta de 14:30 a 16:30 (solapamiento temporal)
    res_2 = reservar_si_es_posible(
        codigo_estudiante=estudiante_habilitado_db.codigo_estudiante,
        nombre_sala=sala_beta.nombre,
        horas=("14:30", "16:30"),
        fecha=hoy,
    )
    assert res_2["estado"] == "RECHAZADA"
    assert "espacio reservado" in res_2["mensaje"]

    # Validar en Mongo que solo existe la reserva en Sala Alfa
    reservas_est = Reserva.objects.filter(estudiante_id=estudiante_habilitado_db.id, fecha=hoy)
    assert reservas_est.count() == 1
    assert reservas_est.first().sala_id == sala_disponible_db.id


def test_10_ciclo_vida_reserva_mongo_consulta_cancelacion_y_liberacion(
    estudiante_habilitado_db, sala_disponible_db
):
    """Integración 10: Ciclo de vida completo: Reserva -> Consulta disponibilidad -> Cancelación -> Reocupación.

    Combina:
        1. `reservar_si_es_posible` para crear reserva en MongoDB.
        2. `consultar_espacios_disponibles` para verificar que la sala quedó ocupada.
        3. `cancelar_reserva` para liberar el espacio en MongoDB.
        4. Verificación en MongoDB del cambio de estado a CANCELADA.
        5. `consultar_espacios_disponibles` comprobando que la sala vuelve a estar libre.
        6. Nueva reserva exitosa en el mismo bloque tras la cancelación.
    """
    hoy = datetime.date.today()
    estudiante_dos, _ = Estudiante.objects.get_or_create(
        codigo_estudiante="TEST-E07",
        defaults={
            "nombres": "Estudiante",
            "apellidos": "Siete",
            "esta_activo": True,
            "matricula_pagada": True,
        },
    )

    # Paso 1: Estudiante 1 reserva la sala
    res_1 = reservar_si_es_posible(
        codigo_estudiante=estudiante_habilitado_db.codigo_estudiante,
        nombre_sala=sala_disponible_db.nombre,
        horas=("16:00", "18:00"),
        fecha=hoy,
    )
    assert res_1["estado"] == "CONFIRMADA"
    id_reserva = res_1["id_reserva"]

    # Paso 2: Consultar disponibilidad -> La sala NO debe estar disponible
    libres = consultar_espacios_disponibles("16:00", "18:00", fecha=hoy)
    assert sala_disponible_db.nombre not in libres

    # Paso 3: Estudiante 2 intenta reservar la misma sala -> Rechazado
    res_rechazada = reservar_si_es_posible(
        codigo_estudiante=estudiante_dos.codigo_estudiante,
        nombre_sala=sala_disponible_db.nombre,
        horas=("16:00", "18:00"),
        fecha=hoy,
    )
    assert res_rechazada["estado"] == "RECHAZADA"

    # Paso 4: Cancelar la reserva del Estudiante 1
    cancelacion = cancelar_reserva(
        codigo_estudiante=estudiante_habilitado_db.codigo_estudiante,
        nombre_sala=sala_disponible_db.nombre,
        fecha=hoy,
    )
    assert cancelacion["estado"] == "EXITO"

    # Validar en MongoDB que el estado de la reserva pasó a CANCELADA
    reserva_db = Reserva.objects.get(id=id_reserva)
    assert reserva_db.estado == Reserva.ESTADO_CANCELADA

    # Paso 5: Consultar disponibilidad -> La sala DEBE aparecer nuevamente disponible
    libres_tras_cancelar = consultar_espacios_disponibles("16:00", "18:00", fecha=hoy)
    assert sala_disponible_db.nombre in libres_tras_cancelar

    # Paso 6: Ahora Estudiante 2 puede reservar la sala liberada con éxito
    res_2 = reservar_si_es_posible(
        codigo_estudiante=estudiante_dos.codigo_estudiante,
        nombre_sala=sala_disponible_db.nombre,
        horas=("16:00", "18:00"),
        fecha=hoy,
    )
    assert res_2["estado"] == "CONFIRMADA"
