"""
tests/test_reglas.py
====================
Pruebas de comportamiento para las reglas de negocio del sistema de reservas:
  - Creación de reservas con capacidad y disponibilidad.
  - Validación del margen obligatorio de desalojo (15 minutos).
  - Prevención de doble reserva simultánea para un mismo estudiante.
  - Consulta de espacios disponibles.
  - Cancelación de reservas activas.
"""

from proyecto.clases.sala import Sala
from proyecto.clases.estudiante import Estudiante
from proyecto.clases.sistema_reservas import SistemaReservas

import pytest

# Este módulo usa MongoDB (SistemaReservas consulta la base antes del modo en memoria): corre sobre la base de pruebas (test_...), nunca sobre la real.
pytestmark = pytest.mark.usefixtures("limpiar_reservas_test")


def test_crear_reserva_exitosa_si_hay_capacidad_y_disponibilidad():
    """Valida que una reserva válida se confirme exitosamente si la sala está libre y tiene capacidad."""
    sistema = SistemaReservas()
    sistema.agregar_sala(Sala("A", 6))
    estudiante = Estudiante(92345)

    resultado = sistema.crear_reserva(
        estudiante=estudiante,
        id_sala="A",
        hora_inicio="10:00",
        hora_fin="12:00",
        asistentes=4,
    )
    assert resultado["estado"] == "CONFIRMADA"


def test_rechaza_reserva_si_no_respeta_15_minutos_de_desalojo():
    """Valida que se rechace una reserva si entre la anterior y la nueva hay menos de 15 minutos de margen."""
    sistema = SistemaReservas()
    sistema.agregar_sala(Sala("A", 6))
    estudiante_previo = Estudiante(11111)
    estudiante_nuevo = Estudiante(92345)

    sistema.crear_reserva(estudiante_previo, "A", "07:45", "09:45", 4)

    resultado = sistema.crear_reserva(
        estudiante=estudiante_nuevo,
        id_sala="A",
        hora_inicio="09:50",
        hora_fin="12:00",
        asistentes=4,
    )
    assert resultado["estado"] == "RECHAZADA"
    assert "15 minutos" in resultado["mensaje"]


def test_rechaza_si_estudiante_ya_tiene_reserva_en_otra_sala_mismo_bloque():
    """Valida que un estudiante no pueda reservar dos salas diferentes en el mismo horario."""
    sistema = SistemaReservas()
    sistema.agregar_sala(Sala("A", 6))
    sistema.agregar_sala(Sala("B", 4))
    estudiante = Estudiante(92345)

    sistema.crear_reserva(estudiante, "B", "10:00", "12:00", 2)

    resultado = sistema.crear_reserva(
        estudiante=estudiante,
        id_sala="A",
        hora_inicio="10:00",
        hora_fin="12:00",
        asistentes=3,
    )
    assert resultado["estado"] == "RECHAZADA"
    assert "espacio reservado" in resultado["mensaje"]


def test_consultar_espacios_disponibles():
    """Valida la consulta de salas libres excluyendo aquellas ocupadas en el intervalo."""
    sistema = SistemaReservas()
    sistema.agregar_sala(Sala("A", 6))
    sistema.agregar_sala(Sala("B", 4))
    sistema.agregar_sala(Sala("C", 10))

    sistema.crear_reserva(Estudiante(11111), "A", "10:00", "12:00", 2)

    disponibles = sistema.consultar_espacios_disponibles("10:30", "11:30")

    assert "A" not in disponibles
    assert "B" in disponibles
    assert "C" in disponibles


def test_cancelar_reserva_exitosa():
    """Valida que la cancelación de una reserva existente elimine el registro y libere el espacio."""
    sistema = SistemaReservas()
    sistema.agregar_sala(Sala("A", 6))
    estudiante = Estudiante(92345)

    sistema.crear_reserva(estudiante, "A", "10:00", "12:00", 4)
    resultado = sistema.cancelar_reserva(92345, "A")

    assert resultado["estado"] == "EXITO"
    assert len(sistema.reservas) == 0


def test_cancelar_reserva_rechazada_si_no_existe():
    """Valida que intentar cancelar una reserva inexistente retorne un estado de rechazo."""
    sistema = SistemaReservas()
    sistema.agregar_sala(Sala("A", 6))
    sistema.crear_reserva(Estudiante(11111), "A", "10:00", "12:00", 4)

    resultado = sistema.cancelar_reserva(99999, "A")

    assert resultado["estado"] == "RECHAZADA"
    assert len(sistema.reservas) == 1