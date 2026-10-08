"""
tests/test_padron.py
====================
Padrón simulado de la UPB (DB estática de la pizarra), registro e inicio de sesión.

Recorridos que explicó el docente:
    REGISTRO:       FE → MW → DB estática (padrón) → DB del proyecto
    INICIAR SESIÓN: FE → MW → DB del proyecto   (el padrón ya no interviene)
"""

import re

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from django.utils import timezone

import reservas.padron as padron
from reservas.models import Estudiante, Reserva
from reservas.padron import buscar_en_padron, cargar_padron
from reservas.permisos import es_duenio_de_reserva

from conftest import CLAVE_TEST

PADRON_EJEMPLO = [
    {"codigo": "11111", "nombres": "Ana", "apellidos": "Paz", "email": "ana.paz@est.upb.example",
     "rol": "estudiante", "nivel": "pregrado", "carrera": "ISC", "activo": True, "matricula_vigente": True},
]


# ---------------------------------------------------------------------------
# Pruebas puras (sin MongoDB)
# ---------------------------------------------------------------------------

def test_busca_por_codigo_y_correo_sin_distinguir_mayusculas():
    assert buscar_en_padron("11111", "ANA.PAZ@est.upb.example", PADRON_EJEMPLO)["nombres"] == "Ana"


def test_correo_que_no_corresponde_al_codigo_no_entra():
    assert buscar_en_padron("11111", "otra.persona@est.upb.example", PADRON_EJEMPLO) is None


def test_datos_vacios_no_entran():
    assert buscar_en_padron("", "", PADRON_EJEMPLO) is None


def test_padron_del_repositorio_es_ficticio_y_consistente():
    personas = cargar_padron()
    codigos = [p["codigo"] for p in personas]
    assert len(personas) == 19
    assert len(set(codigos)) == len(codigos), "códigos repetidos"
    # Los códigos de la UPB tienen 5 dígitos.
    assert all(re.fullmatch(r"\d{5}", c) for c in codigos)
    # El repositorio es público: ningún correo puede ser real (.example no existe).
    assert all(p["email"].endswith(".example") for p in personas)
    # El padrón no guarda contraseñas: cada persona elige la suya al registrarse.
    assert all("password" not in p and "password_hash" not in p for p in personas)


def test_padron_del_repositorio_tiene_todos_los_roles_y_niveles():
    personas = cargar_padron()
    assert {p["rol"] for p in personas} == {"estudiante", "docente", "admin"}
    estudiantes = [p for p in personas if p["rol"] == "estudiante"]
    assert {p["nivel"] for p in estudiantes} == {"pregrado", "postgrado", "doctorado"}
    # Docente y administradores no tienen nivel académico.
    assert all(p["nivel"] is None for p in personas if p["rol"] != "estudiante")


def test_duenio_por_codigo_de_estudiante():
    reserva = Reserva(estudiante=Estudiante(codigo_estudiante="94210", nombres="Lucía", apellidos="Méndez"))
    assert es_duenio_de_reserva(User(username="94210"), reserva)
    assert not es_duenio_de_reserva(User(username="93815"), reserva)


# ---------------------------------------------------------------------------
# Registro (consulta el padrón y crea la cuenta en la base del proyecto)
# ---------------------------------------------------------------------------

def _registrar(cliente, codigo, email, password=CLAVE_TEST, repetir=None):
    return cliente.post("/registro/", {
        "codigo": codigo, "email": email, "password": password,
        "password2": password if repetir is None else repetir,
    })


@pytest.mark.usefixtures("limpiar_reservas_test")
def test_registro_crea_la_cuenta_con_los_datos_del_padron():
    respuesta = _registrar(Client(), "94210", "lucia.mendez@est.upb.example")
    assert respuesta.status_code == 302
    assert respuesta["Location"] == reverse("login") + "?registrado=1"
    usuario = User.objects.get(username="94210")
    assert usuario.check_password(CLAVE_TEST)
    assert usuario.password != CLAVE_TEST and usuario.password.startswith("pbkdf2_sha256$")  # solo el hash
    estudiante = Estudiante.objects.get(codigo_estudiante="94210")
    assert (estudiante.nivel, estudiante.matricula_pagada, estudiante.esta_activo) == ("pregrado", True, True)


@pytest.mark.usefixtures("limpiar_reservas_test")
def test_registro_de_postgrado_guarda_su_nivel_y_el_de_carlos_su_matricula():
    _registrar(Client(), "81247", "patricia.aguilera@est.upb.example")
    _registrar(Client(), "94377", "carlos.torrico@est.upb.example")
    assert Estudiante.objects.get(codigo_estudiante="81247").nivel == "postgrado"
    assert Estudiante.objects.get(codigo_estudiante="94377").matricula_pagada is False  # viene del padrón


@pytest.mark.usefixtures("limpiar_reservas_test")
@pytest.mark.parametrize("codigo, email, es_staff", [
    ("20011", "sergio.barrientos@upb.example", True),   # docente
    ("20013", "raul.vaca@upb.example", True),           # administrador
    ("94210", "lucia.mendez@est.upb.example", False),   # estudiante
])
def test_el_rol_del_padron_decide_los_permisos(codigo, email, es_staff):
    _registrar(Client(), codigo, email)
    usuario = User.objects.get(username=codigo)
    assert usuario.is_staff is es_staff
    assert usuario.is_superuser is False  # el padrón nunca da superusuario
    # El personal no es estudiante: no se crea un Estudiante para él.
    assert Estudiante.objects.filter(codigo_estudiante=codigo).exists() is (not es_staff)


@pytest.mark.usefixtures("limpiar_reservas_test")
@pytest.mark.parametrize("codigo, email, texto", [
    ("99999", "nadie@est.upb.example", "No figuras en el padrón"),               # no figura
    ("94210", "otro.correo@est.upb.example", "No figuras en el padrón"),         # correo no corresponde
    ("92604", "sebastian.gutierrez@est.upb.example", "no está activo"),          # inactivo
    ("U-9421", "lucia.mendez@est.upb.example", "5 dígitos"),                     # formato de código
])
def test_registro_rechaza_a_quien_no_corresponde(codigo, email, texto):
    respuesta = _registrar(Client(), codigo, email)
    assert respuesta.status_code == 200
    assert texto in respuesta.content.decode()
    assert not User.objects.filter(username=codigo).exists()


@pytest.mark.usefixtures("limpiar_reservas_test")
def test_registro_rechaza_contrasenas_distintas_o_debiles():
    distintas = _registrar(Client(), "94210", "lucia.mendez@est.upb.example", repetir="otra-clave-2026")
    assert "no coinciden" in distintas.content.decode()
    for debil in ("12345678", "password", "corta"):
        respuesta = _registrar(Client(), "94210", "lucia.mendez@est.upb.example", password=debil)
        assert respuesta.status_code == 200
    assert not User.objects.filter(username="94210").exists()


@pytest.mark.usefixtures("limpiar_reservas_test")
def test_no_se_puede_registrar_dos_veces_ni_cambiar_la_contrasena_de_otro():
    _registrar(Client(), "94210", "lucia.mendez@est.upb.example")
    intruso = _registrar(Client(), "94210", "lucia.mendez@est.upb.example", password="Otra-clave-2026-x")
    assert "ya tiene una cuenta" in intruso.content.decode()
    assert User.objects.get(username="94210").check_password(CLAVE_TEST)  # sigue siendo la original


# ---------------------------------------------------------------------------
# Inicio de sesión (solo la base del proyecto)
# ---------------------------------------------------------------------------

def _entrar(cliente, codigo, email, password=CLAVE_TEST):
    return cliente.post("/login/", {"codigo": codigo, "email": email, "password": password})


@pytest.mark.usefixtures("limpiar_reservas_test")
def test_hay_un_solo_formulario_de_inicio_de_sesion_y_un_enlace_al_registro():
    html = Client().get("/login/").content.decode()
    assert 'name="codigo"' in html and 'name="email"' in html and 'name="password"' in html
    assert 'name="username"' not in html          # ya no hay acceso aparte para el personal
    assert "Docente o admin" not in html
    assert reverse("registro") in html


@pytest.mark.usefixtures("limpiar_reservas_test")
@pytest.mark.parametrize("codigo, email, es_staff", [
    ("20011", "sergio.barrientos@upb.example", True),
    ("94210", "lucia.mendez@est.upb.example", False),
])
def test_despues_de_registrarse_inicia_sesion_y_va_a_su_pantalla(codigo, email, es_staff):
    _registrar(Client(), codigo, email)
    cliente = Client()
    respuesta = _entrar(cliente, codigo, email)
    assert respuesta.status_code == 302
    assert respuesta["Location"] == reverse("admin_dashboard" if es_staff else "inicio")
    assert "_auth_user_id" in cliente.session


@pytest.mark.usefixtures("limpiar_reservas_test")
def test_el_login_no_consulta_el_padron(monkeypatch):
    _registrar(Client(), "94210", "lucia.mendez@est.upb.example")

    def padron_caido(*args, **kwargs):
        raise AssertionError("el inicio de sesión no debe consultar el padrón")

    monkeypatch.setattr(padron, "cargar_padron", padron_caido)
    respuesta = _entrar(Client(), "94210", "lucia.mendez@est.upb.example")
    assert respuesta.status_code == 302


@pytest.mark.usefixtures("limpiar_reservas_test")
def test_estar_en_el_padron_no_basta_para_iniciar_sesion_sin_registrarse():
    cliente = Client()
    respuesta = _entrar(cliente, "94210", "lucia.mendez@est.upb.example")
    assert "Código, correo o contraseña incorrectos" in respuesta.content.decode()
    assert "_auth_user_id" not in cliente.session


@pytest.mark.usefixtures("limpiar_reservas_test")
@pytest.mark.parametrize("codigo, email, password", [
    ("94210", "lucia.mendez@est.upb.example", "contraseña-equivocada"),  # contraseña mal
    ("94210", "otro.correo@est.upb.example", CLAVE_TEST),                 # correo no corresponde
    ("99999", "nadie@est.upb.example", CLAVE_TEST),                       # sin cuenta
])
def test_login_rechaza_con_mensaje_generico(codigo, email, password):
    _registrar(Client(), "94210", "lucia.mendez@est.upb.example")
    cliente = Client()
    respuesta = _entrar(cliente, codigo, email, password)
    assert respuesta.status_code == 200
    assert "Código, correo o contraseña incorrectos" in respuesta.content.decode()
    assert "_auth_user_id" not in cliente.session


@pytest.mark.usefixtures("limpiar_reservas_test")
def test_login_rechaza_codigo_que_no_tiene_5_digitos():
    respuesta = _entrar(Client(), "U-92004", "lucia.mendez@est.upb.example")
    assert respuesta.status_code == 200
    assert "5 dígitos" in respuesta.content.decode()


def test_estudiante_solo_puede_reservar_a_su_nombre(sala_disponible_db, iniciar_sesion):
    cliente = iniciar_sesion("94210")  # Lucía
    iniciar_sesion("93815")            # Valeria también tiene cuenta
    fecha = timezone.localdate().isoformat()  # hoy: pregrado ya puede reservar para hoy
    respuesta = cliente.post(
        "/api/reservar/",
        {"codigo_estudiante": "93815", "nombre_sala": sala_disponible_db.nombre,
         "hora_inicio": "10:00", "hora_fin": "12:00", "fecha": fecha},
        content_type="application/json",
    ).json()
    assert respuesta["estado"] == "CONFIRMADA"
    reserva = Reserva.objects.get(id=respuesta["id_reserva"])
    assert reserva.estudiante.codigo_estudiante == "94210"  # no la de Valeria (93815)
