"""
tests/test_padron.py
====================
Padrón simulado de la UPB (DB estática de la pizarra) y el inicio de sesión único
(código + correo + contraseña) para estudiantes, docente y administradores.
"""

import datetime
import re

import pytest
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from reservas.models import Estudiante, Reserva
from reservas.padron import buscar_en_padron, cargar_padron, verificar_credenciales
from reservas.permisos import es_duenio_de_reserva

CLAVE_DEMO = "password"

PADRON_EJEMPLO = [
    {"codigo": "11111", "nombres": "Ana", "apellidos": "Paz", "email": "ana.paz@est.upb.example",
     "rol": "estudiante", "nivel": "pregrado", "carrera": "ISC", "activo": True, "matricula_vigente": True,
     "password_hash": make_password("clave-de-ana")},
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


def test_contrasena_correcta_entra_y_la_incorrecta_o_vacia_no():
    assert verificar_credenciales("11111", "ana.paz@est.upb.example", "clave-de-ana", PADRON_EJEMPLO) is not None
    assert verificar_credenciales("11111", "ana.paz@est.upb.example", "otra", PADRON_EJEMPLO) is None
    assert verificar_credenciales("11111", "ana.paz@est.upb.example", "", PADRON_EJEMPLO) is None


def test_persona_sin_hash_en_el_padron_no_puede_entrar():
    sin_hash = [{**PADRON_EJEMPLO[0], "password_hash": ""}]
    assert verificar_credenciales("11111", "ana.paz@est.upb.example", "", sin_hash) is None
    assert verificar_credenciales("11111", "ana.paz@est.upb.example", "cualquiera", sin_hash) is None


def test_padron_del_repositorio_es_ficticio_y_consistente():
    padron = cargar_padron()
    codigos = [p["codigo"] for p in padron]
    assert len(padron) == 19
    assert len(set(codigos)) == len(codigos), "códigos repetidos"
    # Los códigos de la UPB tienen 5 dígitos.
    assert all(re.fullmatch(r"\d{5}", c) for c in codigos)
    # El repositorio es público: ningún correo puede ser real (.example no existe).
    assert all(p["email"].endswith(".example") for p in padron)
    # Nunca se guarda la contraseña, solo su hash.
    assert all(p["password_hash"].startswith("pbkdf2_sha256$") for p in padron)


def test_padron_del_repositorio_tiene_todos_los_roles_y_niveles():
    padron = cargar_padron()
    assert {p["rol"] for p in padron} == {"estudiante", "docente", "admin"}
    estudiantes = [p for p in padron if p["rol"] == "estudiante"]
    assert {p["nivel"] for p in estudiantes} == {"pregrado", "postgrado", "doctorado"}
    # Docente y administradores no tienen nivel académico.
    assert all(p["nivel"] is None for p in padron if p["rol"] != "estudiante")


def test_duenio_por_codigo_de_estudiante():
    reserva = Reserva(estudiante=Estudiante(codigo_estudiante="94210", nombres="Lucía", apellidos="Méndez"))
    assert es_duenio_de_reserva(User(username="94210"), reserva)
    assert not es_duenio_de_reserva(User(username="93815"), reserva)


# ---------------------------------------------------------------------------
# Pruebas con MongoDB (base de pruebas test_...)
# ---------------------------------------------------------------------------

def _entrar(cliente, codigo, email, password=CLAVE_DEMO):
    return cliente.post("/login/", {"codigo": codigo, "email": email, "password": password})


@pytest.mark.usefixtures("limpiar_reservas_test")
def test_hay_un_solo_formulario_de_inicio_de_sesion():
    html = Client().get("/login/").content.decode()
    assert 'name="codigo"' in html and 'name="email"' in html and 'name="password"' in html
    assert 'name="username"' not in html          # ya no hay acceso aparte para el personal
    assert "Docente o admin" not in html


@pytest.mark.usefixtures("limpiar_reservas_test")
def test_login_de_estudiante_crea_su_usuario_y_sincroniza_matricula_y_nivel():
    respuesta = _entrar(Client(), "94377", "carlos.torrico@est.upb.example")
    assert respuesta.status_code == 302
    assert User.objects.filter(username="94377").exists()
    carlos = Estudiante.objects.get(codigo_estudiante="94377")
    assert carlos.matricula_pagada is False  # viene del padrón: matrícula no vigente
    assert carlos.nivel == "pregrado"


@pytest.mark.usefixtures("limpiar_reservas_test")
def test_login_de_postgrado_guarda_su_nivel():
    _entrar(Client(), "81247", "patricia.aguilera@est.upb.example")
    assert Estudiante.objects.get(codigo_estudiante="81247").nivel == "postgrado"


@pytest.mark.usefixtures("limpiar_reservas_test")
@pytest.mark.parametrize("codigo, email, es_staff", [
    ("20011", "sergio.barrientos@upb.example", True),   # docente
    ("20013", "raul.vaca@upb.example", True),           # administrador
    ("94210", "lucia.mendez@est.upb.example", False),   # estudiante
])
def test_el_rol_sale_del_padron_y_decide_a_donde_va(codigo, email, es_staff):
    respuesta = _entrar(Client(), codigo, email)
    assert respuesta.status_code == 302
    usuario = User.objects.get(username=codigo)
    assert usuario.is_staff is es_staff
    assert usuario.is_superuser is False  # el padrón nunca da superusuario
    assert respuesta["Location"] == reverse("admin_dashboard" if es_staff else "inicio")
    # El personal no es estudiante: no se crea un Estudiante para él.
    assert Estudiante.objects.filter(codigo_estudiante=codigo).exists() is (not es_staff)


@pytest.mark.usefixtures("limpiar_reservas_test")
@pytest.mark.parametrize("codigo, email, password", [
    ("94210", "lucia.mendez@est.upb.example", "contraseña-equivocada"),  # contraseña mal
    ("94210", "otro.correo@est.upb.example", CLAVE_DEMO),                 # correo no corresponde
    ("99999", "nadie@est.upb.example", CLAVE_DEMO),                       # no figura
])
def test_login_rechaza_con_mensaje_generico(codigo, email, password):
    cliente = Client()
    respuesta = _entrar(cliente, codigo, email, password)
    assert respuesta.status_code == 200
    assert "Código, correo o contraseña incorrectos" in respuesta.content.decode()
    assert "_auth_user_id" not in cliente.session  # no quedó ninguna sesión iniciada


@pytest.mark.usefixtures("limpiar_reservas_test")
def test_login_rechaza_codigo_que_no_tiene_5_digitos():
    respuesta = _entrar(Client(), "U-92004", "lucia.mendez@est.upb.example")
    assert respuesta.status_code == 200
    assert "5 dígitos" in respuesta.content.decode()


@pytest.mark.usefixtures("limpiar_reservas_test")
def test_login_rechaza_a_estudiante_inactivo_solo_si_la_contrasena_es_correcta():
    con_clave = _entrar(Client(), "92604", "sebastian.gutierrez@est.upb.example")
    assert "no está activo" in con_clave.content.decode()
    sin_clave = _entrar(Client(), "92604", "sebastian.gutierrez@est.upb.example", "mal")
    assert "no está activo" not in sin_clave.content.decode()  # no se revela a un desconocido


def test_estudiante_solo_puede_reservar_a_su_nombre(sala_disponible_db):
    cliente = Client()
    _entrar(cliente, "94210", "lucia.mendez@est.upb.example")
    fecha = (datetime.date.today() + datetime.timedelta(days=30)).isoformat()
    respuesta = cliente.post(
        "/api/reservar/",
        {"codigo_estudiante": "93815", "nombre_sala": sala_disponible_db.nombre,
         "hora_inicio": "10:00", "hora_fin": "12:00", "fecha": fecha},
        content_type="application/json",
    ).json()
    assert respuesta["estado"] == "CONFIRMADA"
    reserva = Reserva.objects.get(id=respuesta["id_reserva"])
    assert reserva.estudiante.codigo_estudiante == "94210"  # no la de Valeria (93815)
