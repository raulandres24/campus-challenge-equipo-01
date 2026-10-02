"""
tests/test_unitarios_simples.py
===============================
Pruebas unitarias simples y aisladas.
Cada función de prueba invoca y valida EXACTAMENTE UNA SOLA FUNCIÓN.
"""

import datetime
import pytest

from proyecto.clases import (
    cancelar_reserva_en_mongo,
    consultar_salas_disponibles_dia,
    convertir_a_minutos,
    guardar_reserva_mongo,
    hay_choque_con_buffer,
    hay_solapamiento_simple,
    minutos_a_time,
    parsear_horas,
    reservarSiesPosible,
    revisar_choque_horario_dia,
    revisar_reserva_estudiante_en_horario,
    validar_estudiante_habilitado,
    validar_rango_horario,
    validar_sala_habilitada,
)
from reservas.models import Reserva


# ==============================================================================
# 1. Pruebas aisladas para módulo: horarios.py
# ==============================================================================

def test_convertir_a_minutos_formato_texto():
    """Prueba aislada: convierte texto '10:30' a 630 minutos."""
    resultado = convertir_a_minutos("10:30")
    assert resultado == 630


def test_convertir_a_minutos_objeto_time():
    """Prueba aislada: convierte objeto datetime.time(7, 45) a 465 minutos."""
    resultado = convertir_a_minutos(datetime.time(7, 45))
    assert resultado == 465


def test_convertir_a_minutos_formato_invalido_lanza_error():
    """Prueba aislada: valida que un formato inválido lance ValueError."""
    with pytest.raises(ValueError):
        convertir_a_minutos("hora_invalida")


def test_minutos_a_time_conversion_correcta():
    """Prueba aislada: convierte 600 minutos al objeto datetime.time(10, 0)."""
    resultado = minutos_a_time(600)
    assert resultado == datetime.time(10, 0)


def test_validar_rango_horario_valido():
    """Prueba aislada: valida que hora inicio menor a fin retorne los minutos."""
    min_ini, min_fin = validar_rango_horario("08:00", "10:00")
    assert min_ini == 480
    assert min_fin == 600


def test_validar_rango_horario_invalido_fin_menor_que_inicio():
    """Prueba aislada: valida que hora fin <= inicio lance ValueError."""
    with pytest.raises(ValueError):
        validar_rango_horario("12:00", "10:00")


def test_hay_choque_con_buffer_dentro_del_margen_15_min():
    """Prueba aislada: detecta choque si la distancia entre reservas es de solo 10 minutos."""
    # Reserva A termina a las 600 (10:00), Reserva B inicia a las 610 (10:10) -> Menor al buffer de 15 min
    choca = hay_choque_con_buffer(480, 600, 610, 720, buffer_min=15)
    assert choca is True


def test_hay_choque_con_buffer_fuera_del_margen_15_min():
    """Prueba aislada: NO detecta choque si se respeta exactamente el buffer de 15 minutos."""
    # Reserva A termina a las 600 (10:00), Reserva B inicia a las 615 (10:15) -> Respeta buffer de 15 min
    choca = hay_choque_con_buffer(480, 600, 615, 720, buffer_min=15)
    assert choca is False


def test_hay_solapamiento_simple_directo():
    """Prueba aislada: detecta cruce de horario directo entre dos intervalos."""
    solapa = hay_solapamiento_simple(600, 720, 660, 780)
    assert solapa is True


def test_parsear_horas_desde_cadena():
    """Prueba aislada: parsea '10:00-12:00' a tupla de objetos datetime.time."""
    h_ini, h_fin = parsear_horas("10:00-12:00")
    assert h_ini == datetime.time(10, 0)
    assert h_fin == datetime.time(12, 0)


# ==============================================================================
# 2. Pruebas aisladas para módulo: estudiante.py (MongoDB)
# ==============================================================================

def test_validar_estudiante_habilitado_exitoso(estudiante_habilitado_db):
    """Prueba aislada: valida estudiante activo y con matrícula al día en MongoDB."""
    habilitado, mensaje, obj = validar_estudiante_habilitado(estudiante_habilitado_db.codigo_estudiante)
    assert habilitado is True
    assert "habilitado" in mensaje
    assert obj.id == estudiante_habilitado_db.id


def test_validar_estudiante_rechazado_si_inactivo(estudiante_inactivo_db):
    """Prueba aislada: rechaza estudiante inactivo consultado en MongoDB."""
    habilitado, mensaje, obj = validar_estudiante_habilitado(estudiante_inactivo_db.codigo_estudiante)
    assert habilitado is False
    assert "no está activo" in mensaje
    assert obj is None


def test_validar_estudiante_rechazado_si_sin_matricula(estudiante_sin_matricula_db):
    """Prueba aislada: rechaza estudiante sin matrícula pagada en MongoDB."""
    habilitado, mensaje, obj = validar_estudiante_habilitado(estudiante_sin_matricula_db.codigo_estudiante)
    assert habilitado is False
    assert "no tiene la matrícula pagada" in mensaje
    assert obj is None


def test_validar_estudiante_rechazado_si_no_existe():
    """Prueba aislada: rechaza estudiante inexistente en MongoDB."""
    habilitado, mensaje, obj = validar_estudiante_habilitado("CODIGO-INEXISTENTE-999")
    assert habilitado is False
    assert "no está registrado" in mensaje
    assert obj is None


# ==============================================================================
# 3. Pruebas aisladas para módulo: sala.py (MongoDB)
# ==============================================================================

def test_validar_sala_habilitada_exitosa(sala_disponible_db):
    """Prueba aislada: valida sala existente y sin mantenimiento en MongoDB."""
    habilitada, mensaje, obj = validar_sala_habilitada(sala_disponible_db.nombre)
    assert habilitada is True
    assert "habilitada" in mensaje
    assert obj.id == sala_disponible_db.id


def test_validar_sala_rechazada_en_mantenimiento(sala_mantenimiento_db):
    """Prueba aislada: rechaza sala en estado de mantenimiento en MongoDB."""
    habilitada, mensaje, obj = validar_sala_habilitada(sala_mantenimiento_db.nombre)
    assert habilitada is False
    assert "en mantenimiento" in mensaje
    assert obj is None


def test_validar_sala_rechazada_si_no_existe():
    """Prueba aislada: rechaza sala inexistente en MongoDB."""
    habilitada, mensaje, obj = validar_sala_habilitada("Sala Inexistente XYZ")
    assert habilitada is False
    assert "no existe" in mensaje
    assert obj is None


# ==============================================================================
# 4. Pruebas aisladas para módulo: reserva.py (MongoDB)
# ==============================================================================

def test_revisar_choque_horario_dia_en_sala_libre(sala_disponible_db):
    """Prueba aislada: verifica que un horario libre en una sala retorne True."""
    hoy = datetime.date.today()
    libre, mensaje = revisar_choque_horario_dia(sala_disponible_db.nombre, hoy, "07:00", "09:00")
    assert libre is True
    assert "Horario libre" in mensaje


def test_revisar_reserva_estudiante_en_horario_libre(estudiante_habilitado_db):
    """Prueba aislada: verifica que el estudiante no tenga cruces de horario."""
    hoy = datetime.date.today()
    sin_cruce, mensaje = revisar_reserva_estudiante_en_horario(
        estudiante_habilitado_db.codigo_estudiante, hoy, "07:00", "09:00"
    )
    assert sin_cruce is True
    assert "no tiene otras reservas" in mensaje


def test_guardar_reserva_mongo_crea_registro(estudiante_habilitado_db, sala_disponible_db):
    """Prueba aislada: valida que guardar_reserva_mongo persista en MongoDB."""
    hoy = datetime.date.today()
    reserva = guardar_reserva_mongo(
        estudiante=estudiante_habilitado_db,
        sala=sala_disponible_db,
        fecha=hoy,
        hora_inicio="07:00",
        hora_fin="09:00",
    )
    # Validar persistencia real en MongoDB
    assert reserva.id is not None
    assert Reserva.objects.filter(id=reserva.id).exists()


def test_cancelar_reserva_en_mongo_inexistente():
    """Prueba aislada: cancelar una reserva inexistente retorna False."""
    exito, mensaje = cancelar_reserva_en_mongo("TEST-INEXISTENTE", "Sala Inexistente")
    assert exito is False
    assert "No se encontró ninguna reserva" in mensaje


def test_consultar_salas_disponibles_dia_retorna_lista(sala_disponible_db):
    """Prueba aislada: consulta salas disponibles para un día y rango horario."""
    hoy = datetime.date.today()
    disponibles = consultar_salas_disponibles_dia(hoy, "07:00", "09:00")
    assert isinstance(disponibles, list)
    assert sala_disponible_db.nombre in disponibles


# ==============================================================================
# 5. Pruebas aisladas para alias camelCase: reservarSiesPosible
# ==============================================================================

def test_alias_reservar_si_es_posible_camel_case(estudiante_habilitado_db, sala_disponible_db):
    """Prueba aislada: verifica que el alias reservarSiesPosible funcione idéntico."""
    resultado = reservarSiesPosible(
        codigo_estudiante=estudiante_habilitado_db.codigo_estudiante,
        nombre_sala=sala_disponible_db.nombre,
        horas=("08:00", "09:30"),
    )
    assert resultado["estado"] == "CONFIRMADA"
    assert resultado["datos"]["sala"] == sala_disponible_db.nombre


# ==============================================================================
# 6. Pruebas aisladas para poderes especiales (permisos.py)
# ==============================================================================

def test_tiene_poderes_especiales_usuarios_designados():
    """Prueba aislada: verifica que Sergio, Hugo, Raúl y Alejandro tengan poderes."""
    from reservas.permisos import tiene_poderes_especiales
    from django.contrib.auth.models import AnonymousUser, User

    assert tiene_poderes_especiales(AnonymousUser()) is False

    u_sergio = User(username="sbarrientos")
    assert tiene_poderes_especiales(u_sergio) is True

    u_hugo = User(username="hzuniga")
    assert tiene_poderes_especiales(u_hugo) is True

    u_raul = User(username="rvaca")
    assert tiene_poderes_especiales(u_raul) is True

    u_alejandro = User(username="aparraga")
    assert tiene_poderes_especiales(u_alejandro) is True

    u_normal = User(username="estudiante.comun")
    assert tiene_poderes_especiales(u_normal) is False


def test_obtener_info_usuario_formato_correcto():
    """Prueba aislada: valida que obtener_info_usuario devuelva la insignia y rol adecuados."""
    from reservas.permisos import obtener_info_usuario
    from django.contrib.auth.models import User

    u_docente = User(username="sbarrientos", first_name="Sergio", last_name="Barrientos")
    info = obtener_info_usuario(u_docente)
    assert info["tiene_poderes"] is True
    assert "INGENIERO DOCENTE" in info["insignia"]

