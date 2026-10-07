"""
tests/test_agenda.py
====================
Pruebas puras (sin MongoDB) de la agenda del día y de la pantalla del estudiante.
"""

import datetime
from types import SimpleNamespace

from django.template.loader import render_to_string
from django.test import RequestFactory
from django.urls import resolve

from reservas.agenda import armar_agenda
from reservas.views import BLOQUES_PREDEFINIDOS

ALFA = SimpleNamespace(id="s1", nombre="Sala Alfa", en_mantenimiento=False)
GAMMA = SimpleNamespace(id="s2", nombre="Sala Gamma", en_mantenimiento=True)


def _reserva(ini, fin, **extra):
    datos = {
        "id": "r1", "sala_nombre": "Sala Alfa", "hora_inicio": ini, "hora_fin": fin,
        "estudiante_nombre": "Lucía Méndez", "estudiante_codigo": "U-92004",
        "color_border": "#10b981", "es_propia": True, "puede_gestionar": True,
        "ya_comenzo": False, "fecha": "2030-01-15",
    }
    datos.update(extra)
    return datos


def _celda(por_sala, inicio_bloque, indice_sala=0):
    return next(c for c in por_sala[indice_sala]["celdas"] if c["bloque"]["inicio"] == inicio_bloque)


def test_reserva_movida_fuera_de_bloque_sigue_visible():
    # Movida a 08:00–09:30 (caso "Normal"): no empieza en un bloque, pero debe verse.
    _, por_sala = armar_agenda([ALFA], [_reserva("08:00", "09:30")], BLOQUES_PREDEFINIDOS)
    assert len(_celda(por_sala, "07:45")["reservas"]) == 1
    assert _celda(por_sala, "10:00")["libre"] is True


def test_reserva_que_cruza_dos_bloques_ocupa_ambos():
    _, por_sala = armar_agenda([ALFA], [_reserva("11:00", "13:00")], BLOQUES_PREDEFINIDOS)
    assert not _celda(por_sala, "10:00")["libre"]
    assert not _celda(por_sala, "12:15")["libre"]


def test_sala_en_mantenimiento_nunca_figura_libre():
    filas, _ = armar_agenda([ALFA, GAMMA], [], BLOQUES_PREDEFINIDOS)
    assert all(fila["celdas"][0]["libre"] for fila in filas)
    assert not any(fila["celdas"][1]["libre"] for fila in filas)


def _render_inicio(reservas):
    filas, por_sala = armar_agenda([ALFA], reservas, BLOQUES_PREDEFINIDOS)
    contexto = {
        "user_info": {"nombre_completo": "Lucía Méndez", "rol": "Estudiante", "tiene_poderes": False},
        "tiene_poderes": False, "hoy": datetime.date(2030, 1, 15), "fecha_iso": "2030-01-15",
        "fecha_formateada": "15 de enero de 2030", "dia_nombre": "Martes", "salas": [ALFA],
        "filas_agenda": filas, "agenda_por_sala": por_sala, "bloques_predefinidos": BLOQUES_PREDEFINIDOS,
        "estudiante_asociado": None, "estudiantes_habilitados": [],
    }
    peticion = RequestFactory().get("/")
    peticion.user = SimpleNamespace(is_authenticated=True, first_name="Lucía", last_name="Méndez")
    peticion.resolver_match = resolve("/")
    return render_to_string("web/inicio.html", contexto, request=peticion)


def test_pantalla_muestra_modificar_en_reserva_propia_no_iniciada():
    html = _render_inicio([_reserva("10:00", "12:00")])
    assert 'onclick="abrirModificar(this)"' in html
    assert "¿Deseas mantenerla?" in html


def test_pantalla_oculta_modificar_si_la_reserva_ya_comenzo():
    html = _render_inicio([_reserva("10:00", "12:00", ya_comenzo=True)])
    assert 'onclick="abrirModificar(this)"' not in html
    assert "Ya comenzó" in html
