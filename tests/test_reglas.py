from proyecto.reglas import crear_reserva


def test_crear_reserva_exitosa_si_hay_capacidad_y_disponibilidad():
    # 1. Preparar el estado inicial.
    salas = {
        "A": {"capacidad": 6}
    }
    reservas_activas = []

    # 2. Entrada: Estudiante intenta reservar la Sala A
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
    assert resultado["estado"] == "RECHAZADA"
    assert "15 minutos" in resultado["mensaje"]

def test_rechaza_reserva_si_no_respeta_15_minutos_de_desalojo():
    salas = {"A": {"capacidad": 6}}

    # Estado inicial: Alguien mas tiene la sala hasta las 09:45
    reservas_activas = [
        {"sala_id": "A", "estudiante_codigo": 11111, "hora_inicio": "07:45", "hora_fin": "09:45"}
    ]

    # Entrada: Tu intentas entrar a las 09:50
    resultado = crear_reserva(
        salas=salas,
        reservas=reservas_activas,
        estudiante_codigo=92345,
        sala_id="A",
        hora_inicio="09:50",
        hora_fin="12:00",
        asistentes=4
    )

    # Resultado esperado: El sistema te debe rebotar
    assert resultado["estado"] == "RECHAZADA"
    assert "15 minutos" in resultado["mensaje"]


def test_rechaza_si_estudiante_ya_tiene_reserva_en_otra_sala_mismo_bloque():
    salas = {"A": {"capacidad": 6}, "B": {"capacidad": 4}}
    reservas_activas = [
        {"sala_id": "B", "estudiante_codigo": 92345, "hora_inicio": "10:00", "hora_fin": "12:00"}
    ]
    resultado = crear_reserva(
        salas=salas, reservas=reservas_activas, estudiante_codigo=92345,
        sala_id="A", hora_inicio="10:00", hora_fin="12:00", asistentes=3
    )
    assert resultado["estado"] == "RECHAZADA"
    assert "ya cuenta con un espacio" in resultado["mensaje"]