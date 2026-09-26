"""Pruebas iniciales.

Comprueban solo algunos de los comportamientos requeridos.
"""
from proyecto.reglas import crear_reserva


def test_crear_reserva_exitosa_si_hay_capacidad_y_disponibilidad():
    # 1. Preparar el estado inicial (Datos simulados en memoria)
    salas = {
        "A": {"capacidad": 6}
    }
    reservas_activas = []  # Lista vacía, no hay reservas previas

    # 2. Entrada: El estudiante 92345 intenta reservar la Sala A (capacidad 6) para 4 personas
    resultado = crear_reserva(
        salas=salas,
        reservas=reservas_activas,
        estudiante_codigo=92345,
        sala_id="A",
        hora_inicio="10:00",
        hora_fin="12:00",
        asistentes=4
    )

    # 3. Resultado esperado
    assert resultado["estado"] == "CONFIRMADA"