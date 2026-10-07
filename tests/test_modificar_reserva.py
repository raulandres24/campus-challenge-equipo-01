"""
tests/test_modificar_reserva.py
===============================
Pruebas de RES-05 / RES-CU-01: modificar una reserva (fecha y horario).

Casos de docs/sesion-08-09-plan.md (sección 2), basados en la sesión 6:
  Normal, Borde (se solapa con su propio horario anterior), Límite (15 min
  exactos), Rechazo por desalojo (la original queda intacta) y Ya comenzó.

- Las pruebas "puras" (sin base de datos) corren aunque MongoDB esté apagado.
- Las pruebas con MongoDB usan la base de pruebas ``test_...`` (ver conftest.py).
- ``ahora`` se fija a mano para que el resultado no dependa del reloj.
"""

import datetime

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.utils import timezone

from reservas.models import Estudiante, Reserva
from reservas.permisos import es_duenio_de_reserva
from reservas.services import (
    ReservaRechazada,
    ReservaYaComenzo,
    _verificar_no_ha_comenzado,
    modificar_reserva_si_esta_disponible,
)

FECHA = datetime.date(2030, 1, 15)


def _t(texto: str) -> datetime.time:
    return datetime.datetime.strptime(texto, "%H:%M").time()


def _ahora(texto: str) -> datetime.datetime:
    """Momento del día FECHA en la zona horaria del proyecto (America/La_Paz)."""
    return timezone.make_aware(datetime.datetime.combine(FECHA, _t(texto)))


# ---------------------------------------------------------------------------
# Pruebas puras (sin MongoDB)
# ---------------------------------------------------------------------------

def _reserva_en_memoria(inicio="10:00", fin="12:00") -> Reserva:
    return Reserva(fecha=FECHA, hora_inicio=_t(inicio), hora_fin=_t(fin))


def test_no_ha_comenzado_acepta_antes_del_inicio():
    _verificar_no_ha_comenzado(_reserva_en_memoria(), _ahora("09:59"))  # no lanza


def test_ya_comenzo_rechaza_en_el_minuto_exacto_de_inicio():
    with pytest.raises(ReservaYaComenzo):
        _verificar_no_ha_comenzado(_reserva_en_memoria(), _ahora("10:00"))


def test_ya_comenzo_rechaza_si_esta_en_curso():
    with pytest.raises(ReservaYaComenzo, match="ya comenzó"):
        _verificar_no_ha_comenzado(_reserva_en_memoria(), _ahora("10:30"))


def test_duenio_se_reconoce_por_nombre_exacto():
    reserva = Reserva(estudiante=Estudiante(nombres="Lucía", apellidos="Méndez"))
    usuario = User(username="lucia.mendez", first_name="lucía", last_name="Méndez")
    assert es_duenio_de_reserva(usuario, reserva)


def test_usuario_sin_nombre_no_es_duenio_de_ninguna_reserva():
    reserva = Reserva(estudiante=Estudiante(nombres="Lucía", apellidos="Méndez"))
    assert not es_duenio_de_reserva(User(username="sin.nombre"), reserva)


def test_nombre_parcial_no_cuenta_como_duenio():
    reserva = Reserva(estudiante=Estudiante(nombres="Lucía María", apellidos="Méndez"))
    usuario = User(username="lucia", first_name="Lucía", last_name="Méndez")
    assert not es_duenio_de_reserva(usuario, reserva)


# ---------------------------------------------------------------------------
# Pruebas con MongoDB (base de pruebas test_...)
# ---------------------------------------------------------------------------

@pytest.fixture
def r1(estudiante_habilitado_db, sala_disponible_db):
    """R1: reserva del estudiante de prueba, 10:00–12:00 en Test Sala Alfa."""
    return Reserva.objects.create(
        estudiante=estudiante_habilitado_db, sala=sala_disponible_db,
        fecha=FECHA, hora_inicio=_t("10:00"), hora_fin=_t("12:00"),
    )


@pytest.fixture
def r2(sala_disponible_db):
    """R2: reserva de otro estudiante, 14:00–15:00 en la misma sala."""
    otro, _ = Estudiante.objects.get_or_create(
        codigo_estudiante="TEST-E04",
        defaults={"nombres": "Otro", "apellidos": "Estudiante",
                  "esta_activo": True, "matricula_pagada": True},
    )
    return Reserva.objects.create(
        estudiante=otro, sala=sala_disponible_db,
        fecha=FECHA, hora_inicio=_t("14:00"), hora_fin=_t("15:00"),
    )


def _modificar(reserva, inicio, fin, ahora="07:00"):
    return modificar_reserva_si_esta_disponible(
        reserva=reserva, fecha=FECHA,
        hora_inicio=_t(inicio), hora_fin=_t(fin), ahora=_ahora(ahora),
    )


def _horario_guardado(reserva):
    guardada = Reserva.objects.get(pk=reserva.pk)
    return (guardada.fecha, f"{guardada.hora_inicio:%H:%M}", f"{guardada.hora_fin:%H:%M}", guardada.estado)


def test_normal_mover_a_horario_libre_cambia_solo_esa_reserva(r1, r2):
    _modificar(r1, "08:00", "09:30")
    assert _horario_guardado(r1) == (FECHA, "08:00", "09:30", Reserva.ESTADO_CONFIRMADA)
    assert _horario_guardado(r2) == (FECHA, "14:00", "15:00", Reserva.ESTADO_CONFIRMADA)


def test_borde_se_puede_solapar_con_su_propio_horario_anterior(r1):
    _modificar(r1, "11:00", "13:00")
    assert _horario_guardado(r1)[1:3] == ("11:00", "13:00")


def test_limite_15_minutos_exactos_antes_de_otra_reserva_se_acepta(r1, r2):
    _modificar(r1, "12:30", "13:45")
    assert _horario_guardado(r1)[1:3] == ("12:30", "13:45")


def test_rechazo_por_desalojo_conserva_la_reserva_original(r1, r2):
    with pytest.raises(ReservaRechazada, match="15 minutos"):
        _modificar(r1, "12:30", "13:50")
    assert _horario_guardado(r1) == (FECHA, "10:00", "12:00", Reserva.ESTADO_CONFIRMADA)
    assert _horario_guardado(r2) == (FECHA, "14:00", "15:00", Reserva.ESTADO_CONFIRMADA)


def test_rechazo_si_la_reserva_ya_comenzo(r1):
    with pytest.raises(ReservaYaComenzo):
        _modificar(r1, "11:00", "13:00", ahora="10:30")
    assert _horario_guardado(r1) == (FECHA, "10:00", "12:00", Reserva.ESTADO_CONFIRMADA)


def test_reintentar_la_misma_modificacion_no_falla_ni_duplica(r1):
    _modificar(r1, "08:00", "09:30")
    _modificar(r1, "08:00", "09:30")
    assert Reserva.objects.filter(estudiante=r1.estudiante, fecha=FECHA).count() == 1


def test_endpoint_rechazo_devuelve_causa_y_pregunta_si_mantenerla(r1, r2):
    admin, _ = User.objects.get_or_create(username="test-admin", defaults={"is_staff": True})
    cliente = Client()
    cliente.force_login(admin)
    respuesta = cliente.post(
        "/api/modificar-reserva/",
        {"reserva_id": str(r1.pk), "fecha": FECHA.isoformat(), "hora_inicio": "12:30", "hora_fin": "13:50"},
        content_type="application/json",
    ).json()
    assert respuesta["estado"] == "RECHAZADA"
    assert respuesta["preguntar_mantener"] is True
    assert respuesta["pregunta"] == "¿Deseas mantenerla?"
    assert respuesta["datos"]["hora_inicio"] == "10:00"


def test_endpoint_otro_estudiante_no_puede_modificar(r1):
    intruso, _ = User.objects.get_or_create(
        username="test-intruso", defaults={"first_name": "Otro", "last_name": "Estudiante"},
    )
    cliente = Client()
    cliente.force_login(intruso)
    respuesta = cliente.post(
        "/api/modificar-reserva/",
        {"reserva_id": str(r1.pk), "fecha": FECHA.isoformat(), "hora_inicio": "08:00", "hora_fin": "09:30"},
        content_type="application/json",
    )
    assert respuesta.status_code == 403
    assert _horario_guardado(r1)[1:3] == ("10:00", "12:00")
