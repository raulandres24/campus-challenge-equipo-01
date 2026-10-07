"""
tests/test_padron.py
====================
Padrón simulado de la UPB (DB estática de la pizarra) y login de estudiantes.
"""

import datetime

import pytest
from django.contrib.auth.models import User
from django.test import Client

from reservas.models import Estudiante, Reserva
from reservas.padron import buscar_en_padron, cargar_padron
from reservas.permisos import es_duenio_de_reserva

PADRON_EJEMPLO = [
    {"codigo": "U-1", "nombres": "Ana", "apellidos": "Paz", "email": "ana.paz@est.upb.example",
     "carrera": "ISC", "activo": True, "matricula_vigente": True},
]


# ---------------------------------------------------------------------------
# Pruebas puras (sin MongoDB)
# ---------------------------------------------------------------------------

def test_busca_por_codigo_y_correo_sin_distinguir_mayusculas():
    assert buscar_en_padron("u-1", "ANA.PAZ@est.upb.example", PADRON_EJEMPLO)["nombres"] == "Ana"


def test_correo_que_no_corresponde_al_codigo_no_entra():
    assert buscar_en_padron("U-1", "otra.persona@est.upb.example", PADRON_EJEMPLO) is None


def test_datos_vacios_no_entran():
    assert buscar_en_padron("", "", PADRON_EJEMPLO) is None


def test_padron_del_repositorio_es_ficticio_y_consistente():
    padron = cargar_padron()
    codigos = [p["codigo"] for p in padron]
    assert len(padron) == 15
    assert len(set(codigos)) == len(codigos), "códigos repetidos"
    # El repositorio es público: ningún correo puede ser real (.example no existe).
    assert all(p["email"].endswith(".example") for p in padron)


def test_duenio_por_codigo_de_estudiante():
    reserva = Reserva(estudiante=Estudiante(codigo_estudiante="U-92004", nombres="Lucía", apellidos="Méndez"))
    assert es_duenio_de_reserva(User(username="U-92004"), reserva)
    assert not es_duenio_de_reserva(User(username="U-92006"), reserva)


# ---------------------------------------------------------------------------
# Pruebas con MongoDB (base de pruebas test_...)
# ---------------------------------------------------------------------------

def _entrar(cliente, codigo, email):
    return cliente.post("/login/", {"modo": "estudiante", "codigo": codigo, "email": email})


@pytest.mark.usefixtures("limpiar_reservas_test")
def test_login_de_estudiante_del_padron_crea_su_usuario_y_sincroniza_matricula():
    respuesta = _entrar(Client(), "U-92005", "carlos.torrico@est.upb.example")
    assert respuesta.status_code == 302
    assert User.objects.filter(username="U-92005").exists()
    carlos = Estudiante.objects.get(codigo_estudiante="U-92005")
    assert carlos.matricula_pagada is False  # viene del padrón: matrícula no vigente


@pytest.mark.usefixtures("limpiar_reservas_test")
def test_login_rechaza_a_quien_no_figura_en_el_padron():
    respuesta = _entrar(Client(), "U-99999", "nadie@est.upb.example")
    assert respuesta.status_code == 200
    assert "No figuras en el padrón" in respuesta.content.decode()
    assert not User.objects.filter(username="U-99999").exists()


@pytest.mark.usefixtures("limpiar_reservas_test")
def test_login_rechaza_a_estudiante_inactivo():
    respuesta = _entrar(Client(), "U-92007", "sebastian.gutierrez@est.upb.example")
    assert respuesta.status_code == 200
    assert "no está activo" in respuesta.content.decode()


def test_estudiante_solo_puede_reservar_a_su_nombre(sala_disponible_db):
    cliente = Client()
    _entrar(cliente, "U-92004", "lucia.mendez@est.upb.example")
    fecha = (datetime.date.today() + datetime.timedelta(days=30)).isoformat()
    respuesta = cliente.post(
        "/api/reservar/",
        {"codigo_estudiante": "U-92006", "nombre_sala": sala_disponible_db.nombre,
         "hora_inicio": "10:00", "hora_fin": "12:00", "fecha": fecha},
        content_type="application/json",
    ).json()
    assert respuesta["estado"] == "CONFIRMADA"
    reserva = Reserva.objects.get(id=respuesta["id_reserva"])
    assert reserva.estudiante.codigo_estudiante == "U-92004"  # no la de Valeria (U-92006)
