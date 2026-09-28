from proyecto.modificaciones import modificar_reserva


def _escenario():
    salas = {"A": {"capacidad": 6}, "B": {"capacidad": 4}}
    reservas = [
        {"sala_id": "A", "estudiante_codigo": 92345, "hora_inicio": "10:00",
         "hora_fin": "12:00", "asistentes": 4},
        {"sala_id": "A", "estudiante_codigo": 11111, "hora_inicio": "14:00",
         "hora_fin": "16:00", "asistentes": 2},
    ]
    return salas, reservas


def test_modificacion_valida_actualiza_la_reserva():
    salas, reservas = _escenario()
    resultado = modificar_reserva(
        salas, reservas, 92345, "A", "10:00",
        nueva_hora_inicio="08:00", nueva_hora_fin="09:30",
    )
    assert resultado["estado"] == "MODIFICADA"
    assert reservas[0]["hora_inicio"] == "08:00"
    assert reservas[0]["hora_fin"] == "09:30"
    assert reservas[0]["asistentes"] == 4  # lo no indicado se conserva


def test_modificacion_invalida_conserva_la_reserva_original():
    salas, reservas = _escenario()
    original = dict(reservas[0])
    # 13:50 no respeta los 15 min antes de la reserva de las 14:00
    resultado = modificar_reserva(
        salas, reservas, 92345, "A", "10:00",
        nueva_hora_inicio="12:30", nueva_hora_fin="13:50",
    )
    assert resultado["estado"] == "RECHAZADA"
    assert reservas[0] == original


def test_limite_exacto_de_15_minutos_se_acepta():
    salas, reservas = _escenario()
    resultado = modificar_reserva(
        salas, reservas, 92345, "A", "10:00",
        nueva_hora_inicio="12:30", nueva_hora_fin="13:45",
    )
    assert resultado["estado"] == "MODIFICADA"


def test_la_reserva_no_choca_consigo_misma():
    salas, reservas = _escenario()
    # Mismo horario, solo cambian los asistentes
    resultado = modificar_reserva(salas, reservas, 92345, "A", "10:00", nuevos_asistentes=5)
    assert resultado["estado"] == "MODIFICADA"
    assert reservas[0]["asistentes"] == 5


def test_rechaza_si_los_nuevos_asistentes_superan_la_capacidad():
    salas, reservas = _escenario()
    original = dict(reservas[0])
    resultado = modificar_reserva(salas, reservas, 92345, "A", "10:00", nuevos_asistentes=7)
    assert resultado["estado"] == "RECHAZADA"
    assert "capacidad" in resultado["mensaje"]
    assert reservas[0] == original


def test_asistentes_igual_a_la_capacidad_exacta_se_acepta():
    salas, reservas = _escenario()
    resultado = modificar_reserva(salas, reservas, 92345, "A", "10:00", nuevos_asistentes=6)
    assert resultado["estado"] == "MODIFICADA"


def test_rechaza_si_la_reserva_no_existe():
    salas, reservas = _escenario()
    resultado = modificar_reserva(salas, reservas, 99999, "A", "10:00", nuevos_asistentes=3)
    assert resultado["estado"] == "RECHAZADA"
    assert "No existe" in resultado["mensaje"]


def test_rechaza_si_el_estudiante_quedaria_con_dos_salas_a_la_vez():
    salas, reservas = _escenario()
    reservas.append({"sala_id": "B", "estudiante_codigo": 92345, "hora_inicio": "16:30",
                     "hora_fin": "18:00", "asistentes": 2})
    # Intenta mover su reserva de la sala A a las 16:45, cuando ya tiene la sala B
    resultado = modificar_reserva(
        salas, reservas, 92345, "A", "10:00",
        nueva_hora_inicio="16:45", nueva_hora_fin="17:30",
    )
    assert resultado["estado"] == "RECHAZADA"
    assert "ya cuenta con un espacio" in resultado["mensaje"]


def test_rechaza_hora_fin_anterior_a_hora_inicio():
    salas, reservas = _escenario()
    resultado = modificar_reserva(
        salas, reservas, 92345, "A", "10:00",
        nueva_hora_inicio="12:00", nueva_hora_fin="11:00",
    )
    assert resultado["estado"] == "RECHAZADA"
