def convertir_a_minutos(hora_texto):
    """Convierte una hora en formato 'HH:MM' a minutos totales (entero)."""
    pass

def crear_reserva(salas, reservas, estudiante_codigo, sala_id, hora_inicio, hora_fin, asistentes):
    """
    Intenta crear una reserva.
    Retorna un diccionario con 'estado' (CONFIRMADA/RECHAZADA) y un 'mensaje'.
    """
    pass

def convertir_a_minutos(hora_texto):
    """Convierte una hora en formato 'HH:MM' a minutos totales (entero)."""
    # La dejaremos en 'pass' por ahora porque aún no validamos horas
    pass


def crear_reserva(salas, reservas, estudiante_codigo, sala_id, hora_inicio, hora_fin, asistentes):
    """
    Intenta crear una reserva.
    Retorna un diccionario con 'estado' (CONFIRMADA/RECHAZADA) y un 'mensaje'.
    """
    # 1. Verificar que la sala exista en nuestro diccionario
    if sala_id not in salas:
        return {"estado": "RECHAZADA", "mensaje": "La sala solicitada no existe."}

    # 2. Verificar la regla de capacidad
    capacidad_maxima = salas[sala_id]["capacidad"]
    if asistentes > capacidad_maxima:
        return {"estado": "RECHAZADA", "mensaje": "La cantidad de asistentes supera la capacidad de la sala."}

    # Si pasa las validaciones (por ahora), la confirmamos
    return {"estado": "CONFIRMADA", "mensaje": "Reserva exitosa."}