"""
tests/test_ventanas.py
======================
Anticipación para reservar (regla del docente, 07/10/2026):

- Postgrado y doctorado: hasta 2 días de clase adelante, a cualquier hora
  (lunes → hasta el miércoles; viernes → hasta el martes).
- Pregrado: desde las 18:00 reserva el día siguiente (lunes 18:00 → martes).

Semana de los ejemplos: lunes 05/10/2026 … viernes 09/10, sábado 10, domingo 11,
lunes 12, martes 13, miércoles 14.
"""

import datetime
from datetime import date, datetime as dt, timezone as tz_utc

import pytest
from django.utils import timezone

from reservas.models import Estudiante
from reservas.services import reservar_si_esta_disponible
from reservas.ventanas import (
    apertura_de_reservas,
    dia_de_clase_anterior,
    mensaje_fuera_de_ventana,
    puede_reservar_para,
    ultima_fecha_reservable,
)

LUN, MAR, MIE, JUE, VIE = date(2026, 10, 5), date(2026, 10, 6), date(2026, 10, 7), date(2026, 10, 8), date(2026, 10, 9)
SAB, DOM, LUN2, MAR2, MIE2 = date(2026, 10, 10), date(2026, 10, 11), date(2026, 10, 12), date(2026, 10, 13), date(2026, 10, 14)


# ---------------------------------------------------------------------------
# Pruebas puras (sin MongoDB)
# ---------------------------------------------------------------------------

def test_dias_de_clase_no_cuentan_sabado_ni_domingo():
    assert dia_de_clase_anterior(MIE, 2) == LUN
    assert dia_de_clase_anterior(MAR2, 2) == VIE       # martes → lunes → viernes
    assert dia_de_clase_anterior(LUN2, 1) == VIE
    assert dia_de_clase_anterior(SAB, 1) == VIE


@pytest.mark.parametrize("nivel", ["postgrado", "doctorado"])
@pytest.mark.parametrize("ahora, permitidas, negadas", [
    # lunes, a cualquier hora: hasta el miércoles todo el día
    (dt(2026, 10, 5, 0, 0), [LUN, MAR, MIE], [JUE]),
    (dt(2026, 10, 5, 23, 59), [LUN, MAR, MIE], [JUE, VIE]),
    # viernes: hasta el martes
    (dt(2026, 10, 9, 8, 0), [VIE, SAB, DOM, LUN2, MAR2], [MIE2]),
    # el domingo cuenta como antes del lunes: todavía no se abre el miércoles
    (dt(2026, 10, 4, 23, 59), [LUN, MAR], [MIE]),
])
def test_posgrado_reserva_hasta_dos_dias_de_clase_adelante(nivel, ahora, permitidas, negadas):
    assert all(puede_reservar_para(nivel, d, ahora) for d in permitidas)
    assert not any(puede_reservar_para(nivel, d, ahora) for d in negadas)


@pytest.mark.parametrize("ahora, permitidas, negadas", [
    # lunes antes de las 18:00: solo hoy; a las 18:00 se abre el martes
    (dt(2026, 10, 5, 17, 59), [LUN], [MAR]),
    (dt(2026, 10, 5, 18, 0), [LUN, MAR], [MIE]),
    (dt(2026, 10, 5, 23, 30), [MAR], [MIE]),
    # viernes: a las 18:00 se abre el próximo día de clase (lunes)
    (dt(2026, 10, 9, 17, 59), [VIE], [LUN2]),
    (dt(2026, 10, 9, 18, 0), [VIE, LUN2], [MAR2]),
    # el sábado ya está abierto el lunes, pero no el martes
    (dt(2026, 10, 10, 10, 0), [LUN2], [MAR2]),
])
def test_pregrado_reserva_el_dia_siguiente_desde_las_18(ahora, permitidas, negadas):
    assert all(puede_reservar_para("pregrado", d, ahora) for d in permitidas)
    assert not any(puede_reservar_para("pregrado", d, ahora) for d in negadas)


def test_la_hora_se_interpreta_en_la_paz_cuando_viene_con_zona():
    # 21:59 UTC = 17:59 en La Paz (UTC-4); 22:00 UTC = 18:00.
    assert not puede_reservar_para("pregrado", MAR, dt(2026, 10, 5, 21, 59, tzinfo=tz_utc.utc))
    assert puede_reservar_para("pregrado", MAR, dt(2026, 10, 5, 22, 0, tzinfo=tz_utc.utc))


def test_apertura_de_reservas():
    assert apertura_de_reservas("pregrado", MAR) == dt(2026, 10, 5, 18, 0)
    assert apertura_de_reservas("pregrado", LUN2) == dt(2026, 10, 9, 18, 0)
    assert apertura_de_reservas("postgrado", MIE) == dt(2026, 10, 5, 0, 0)
    assert apertura_de_reservas("doctorado", MAR2) == dt(2026, 10, 9, 0, 0)


def test_ultima_fecha_reservable():
    assert ultima_fecha_reservable("postgrado", dt(2026, 10, 5, 10, 0)) == MIE
    assert ultima_fecha_reservable("doctorado", dt(2026, 10, 9, 10, 0)) == MAR2
    assert ultima_fecha_reservable("pregrado", dt(2026, 10, 5, 17, 0)) == LUN
    assert ultima_fecha_reservable("pregrado", dt(2026, 10, 5, 18, 0)) == MAR


def test_mensajes_dicen_cuando_se_abre():
    pregrado = mensaje_fuera_de_ventana("pregrado", MIE)
    assert "miércoles 07/10/2026" in pregrado and "martes 06/10/2026 a las 18:00" in pregrado
    posgrado = mensaje_fuera_de_ventana("postgrado", JUE)
    assert "jueves 08/10/2026" in posgrado and "el martes 06/10/2026" in posgrado


# ---------------------------------------------------------------------------
# Pruebas con MongoDB (base de pruebas test_...)
# ---------------------------------------------------------------------------

def _reservar_api(cliente, nombre_sala, fecha, codigo=None):
    datos = {"nombre_sala": nombre_sala, "hora_inicio": "10:00", "hora_fin": "12:00", "fecha": fecha.isoformat()}
    if codigo:
        datos["codigo_estudiante"] = codigo
    return cliente.post("/api/reservar/", datos, content_type="application/json").json()


def test_pregrado_no_reserva_mas_alla_de_su_ventana(sala_disponible_db, iniciar_sesion):
    cliente = iniciar_sesion("94210")  # Lucía, pregrado
    lejos = timezone.localdate() + datetime.timedelta(days=30)
    respuesta = _reservar_api(cliente, sala_disponible_db.nombre, lejos)
    assert respuesta["estado"] == "RECHAZADA"
    assert "Aún no puedes reservar" in respuesta["mensaje"]


def test_pregrado_si_reserva_para_hoy(sala_disponible_db, iniciar_sesion):
    cliente = iniciar_sesion("94210")
    assert _reservar_api(cliente, sala_disponible_db.nombre, timezone.localdate())["estado"] == "CONFIRMADA"


def test_posgrado_no_reserva_mas_alla_de_sus_dos_dias_de_clase(sala_posgrado_db, iniciar_sesion):
    cliente = iniciar_sesion("81247")  # Patricia, postgrado
    lejos = timezone.localdate() + datetime.timedelta(days=30)
    assert _reservar_api(cliente, sala_posgrado_db.nombre, lejos)["estado"] == "RECHAZADA"
    assert _reservar_api(cliente, sala_posgrado_db.nombre, timezone.localdate())["estado"] == "CONFIRMADA"


def test_administrador_no_tiene_limite_de_anticipacion(sala_disponible_db, estudiante_habilitado_db, iniciar_sesion):
    admin = iniciar_sesion("20013")  # Raúl, administrador
    lejos = timezone.localdate() + datetime.timedelta(days=30)
    respuesta = _reservar_api(admin, sala_disponible_db.nombre, lejos, codigo=estudiante_habilitado_db.codigo_estudiante)
    assert respuesta["estado"] == "CONFIRMADA"


def test_modificar_a_una_fecha_fuera_de_la_ventana_se_rechaza_y_deja_la_original(sala_disponible_db, iniciar_sesion):
    cliente = iniciar_sesion("94210")
    lucia = Estudiante.objects.get(codigo_estudiante="94210")
    hoy = timezone.localdate()
    reserva = reservar_si_esta_disponible(
        estudiante=lucia, sala=sala_disponible_db, fecha=hoy,
        hora_inicio=datetime.time(23, 0), hora_fin=datetime.time(23, 30))
    lejos = hoy + datetime.timedelta(days=30)
    respuesta = cliente.post("/api/modificar-reserva/", {
        "reserva_id": str(reserva.id), "fecha": lejos.isoformat(), "hora_inicio": "23:00", "hora_fin": "23:30",
    }, content_type="application/json").json()
    assert respuesta["estado"] == "RECHAZADA"
    assert "Aún no puedes reservar" in respuesta["mensaje"]
    assert respuesta["preguntar_mantener"] is True
    assert respuesta["datos"]["fecha"] == hoy.isoformat()
    reserva.refresh_from_db()
    assert reserva.fecha == hoy  # la original quedó intacta


def test_la_agenda_dice_hasta_que_dia_puede_reservar(sala_disponible_db, iniciar_sesion):
    html = iniciar_sesion("94210").get("/").content.decode()
    assert "Puedes reservar hasta el" in html
