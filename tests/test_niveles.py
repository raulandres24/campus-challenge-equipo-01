"""
tests/test_niveles.py
=====================
Salas por nivel académico: B, C, D, F, H y J son de pregrado; A y E son exclusivas
de postgrado y doctorado (decisión provisional, ver reservas/niveles.py).
"""

import datetime

import pytest
from django.utils import timezone

from reservas.niveles import mensaje_sala_no_permitida, nivel_puede_usar_sala
from reservas.services import SalaNoPermitida, reservar_si_esta_disponible

DIA = datetime.date.today() + datetime.timedelta(days=30)
DIEZ, DOCE = datetime.time(10, 0), datetime.time(12, 0)


# ---------------------------------------------------------------------------
# Pruebas puras (sin MongoDB)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("nivel, sala_exclusiva, permitido", [
    ("pregrado", False, True),     # pregrado → sala común
    ("pregrado", True, False),     # pregrado → sala A/E
    ("postgrado", True, True),     # postgrado → sala A/E
    ("doctorado", True, True),     # doctorado → sala A/E
    ("postgrado", False, False),   # decisión provisional: solo A y E
    ("doctorado", False, False),
])
def test_tabla_de_niveles_y_salas(nivel, sala_exclusiva, permitido):
    assert nivel_puede_usar_sala(nivel, sala_exclusiva) is permitido


def test_nivel_vacio_se_trata_como_pregrado():
    assert nivel_puede_usar_sala("", False) is True
    assert nivel_puede_usar_sala("", True) is False


def test_mensajes_dicen_que_sala_es_de_quien():
    assert "exclusiva de postgrado y doctorado" in mensaje_sala_no_permitida("pregrado", "Sala A", True)
    assert "es de pregrado" in mensaje_sala_no_permitida("postgrado", "Sala B", False)


# ---------------------------------------------------------------------------
# Pruebas con MongoDB (base de pruebas test_...)
# ---------------------------------------------------------------------------

def test_pregrado_reserva_sala_comun(estudiante_habilitado_db, sala_disponible_db):
    reserva = reservar_si_esta_disponible(
        estudiante=estudiante_habilitado_db, sala=sala_disponible_db,
        fecha=DIA, hora_inicio=DIEZ, hora_fin=DOCE)
    assert reserva.sala == sala_disponible_db


def test_pregrado_no_reserva_sala_exclusiva_de_posgrado(estudiante_habilitado_db, sala_posgrado_db):
    with pytest.raises(SalaNoPermitida):
        reservar_si_esta_disponible(
            estudiante=estudiante_habilitado_db, sala=sala_posgrado_db,
            fecha=DIA, hora_inicio=DIEZ, hora_fin=DOCE)


def test_postgrado_reserva_sala_exclusiva_y_no_la_comun(estudiante_habilitado_db, sala_posgrado_db, sala_disponible_db):
    estudiante_habilitado_db.nivel = "postgrado"
    estudiante_habilitado_db.save()
    reserva = reservar_si_esta_disponible(
        estudiante=estudiante_habilitado_db, sala=sala_posgrado_db,
        fecha=DIA, hora_inicio=DIEZ, hora_fin=DOCE)
    assert reserva.sala == sala_posgrado_db
    with pytest.raises(SalaNoPermitida):
        reservar_si_esta_disponible(
            estudiante=estudiante_habilitado_db, sala=sala_disponible_db,
            fecha=DIA, hora_inicio=datetime.time(14, 30), hora_fin=datetime.time(16, 30))


def _reservar(cliente, nombre_sala):
    return cliente.post(
        "/api/reservar/",
        {"nombre_sala": nombre_sala, "hora_inicio": "10:00", "hora_fin": "12:00", "fecha": timezone.localdate().isoformat()},
        content_type="application/json",
    ).json()


def test_endpoint_pregrado_no_reserva_sala_de_posgrado(sala_posgrado_db, iniciar_sesion):
    cliente = iniciar_sesion("94210")  # Lucía, pregrado
    respuesta = _reservar(cliente, sala_posgrado_db.nombre)
    assert respuesta["estado"] == "RECHAZADA"
    assert "exclusiva de postgrado y doctorado" in respuesta["mensaje"]


def test_endpoint_postgrado_reserva_su_sala(sala_posgrado_db, iniciar_sesion):
    cliente = iniciar_sesion("81247")  # Patricia, postgrado
    assert _reservar(cliente, sala_posgrado_db.nombre)["estado"] == "CONFIRMADA"


def test_cada_estudiante_ve_solo_las_salas_de_su_nivel(sala_disponible_db, sala_posgrado_db, iniciar_sesion):
    pregrado = iniciar_sesion("94210")
    html = pregrado.get("/").content.decode()
    assert sala_disponible_db.nombre in html and sala_posgrado_db.nombre not in html

    posgrado = iniciar_sesion("81247")
    html = posgrado.get("/").content.decode()
    assert sala_posgrado_db.nombre in html and sala_disponible_db.nombre not in html
