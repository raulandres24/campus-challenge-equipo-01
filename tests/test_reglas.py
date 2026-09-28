from proyecto.clases.sala import Sala
from proyecto.clases.estudiante import Estudiante
from proyecto.clases.sistema_reservas import SistemaReservas


def test_crear_reserva_exitosa_si_hay_capacidad_y_disponibilidad():
    sistema = SistemaReservas()
    sistema.agregar_sala(Sala("A", 6))
    estudiante = Estudiante(92345)

    resultado = sistema.crear_reserva(
        estudiante=estudiante,
        id_sala="A",
        hora_inicio="10:00",
        hora_fin="12:00",
        asistentes=4
    )
    assert resultado["estado"] == "CONFIRMADA"


def test_rechaza_reserva_si_no_respeta_15_minutos_de_desalojo():
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
        asistentes=4
    )
    assert resultado["estado"] == "RECHAZADA"
    assert "15 minutos" in resultado["mensaje"]


def test_rechaza_si_estudiante_ya_tiene_reserva_en_otra_sala_mismo_bloque():
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
        asistentes=3
    )
    assert resultado["estado"] == "RECHAZADA"
    assert "espacio reservado" in resultado["mensaje"]


def test_consultar_espacios_disponibles():
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
    sistema = SistemaReservas()
    sistema.agregar_sala(Sala("A", 6))
    estudiante = Estudiante(92345)

    sistema.crear_reserva(estudiante, "A", "10:00", "12:00", 4)
    resultado = sistema.cancelar_reserva(92345, "A")

    assert resultado["estado"] == "EXITO"
    assert len(sistema.reservas) == 0


def test_cancelar_reserva_rechazada_si_no_existe():
    sistema = SistemaReservas()
    sistema.agregar_sala(Sala("A", 6))
    sistema.crear_reserva(Estudiante(11111), "A", "10:00", "12:00", 4)

    resultado = sistema.cancelar_reserva(99999, "A")

    assert resultado["estado"] == "RECHAZADA"
    assert len(sistema.reservas) == 1