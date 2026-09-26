def convertir_a_minutos(hora_texto):
    """Convierte una hora en formato 'HH:MM' a minutos totales (entero)."""
    partes = hora_texto.split(":")
    horas = int(partes[0])
    minutos = int(partes[1])
    return (horas * 60) + minutos


def crear_reserva(salas, reservas, estudiante_codigo, sala_id, hora_inicio, hora_fin, asistentes):
    """
    Intenta crear una reserva.
    Retorna un diccionario con 'estado' (CONFIRMADA/RECHAZADA) y un 'mensaje'.
    """
    # 1. Verificar que la sala exista
    if sala_id not in salas:
        return {"estado": "RECHAZADA", "mensaje": "La sala solicitada no existe."}

    # 2. Verificar la regla de capacidad
    capacidad_maxima = salas[sala_id]["capacidad"]
    if asistentes > capacidad_maxima:
        return {"estado": "RECHAZADA", "mensaje": "La cantidad de asistentes supera la capacidad de la sala."}

    # 3. Verificar cruce de horarios y el margen de 15 minutos de limpieza
    nuevo_inicio = convertir_a_minutos(hora_inicio)
    nuevo_fin = convertir_a_minutos(hora_fin)

    for reserva in reservas:
        if reserva["sala_id"] == sala_id:
            existente_inicio = convertir_a_minutos(reserva["hora_inicio"])
            existente_fin = convertir_a_minutos(reserva["hora_fin"])

            # Si el nuevo inicio es menor al fin anterior + 15 min,
            # y el nuevo fin es mayor al inicio anterior - 15 min, hay un choque.
            if nuevo_inicio < (existente_fin + 15) and nuevo_fin > (existente_inicio - 15):
                return {
                    "estado": "RECHAZADA",
                    "mensaje": "Cruce de horarios o no se respetan los 15 minutos de desalojo."
                }

    # Si pasa todas las validaciones
    return {"estado": "CONFIRMADA", "mensaje": "Reserva exitosa."}