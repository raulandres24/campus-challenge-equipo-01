def convertir_a_minutos(hora_texto):
    partes = hora_texto.split(":")
    return int(partes[0]) * 60 + int(partes[1])


def _hay_conflicto_horario(reservas, sala_id, nuevo_inicio, nuevo_fin, buffer_min=15):
    for r in reservas:
        if r["sala_id"] != sala_id:
            continue
        existente_inicio = convertir_a_minutos(r["hora_inicio"])
        existente_fin = convertir_a_minutos(r["hora_fin"])
        if nuevo_inicio < (existente_fin + buffer_min) and nuevo_fin > (existente_inicio - buffer_min):
            return True
    return {"estado": "RECHAZADA", "mensaje": "Cruce de horarios o no se respetan los 15 minutos de desalojo."}


def _estudiante_ya_reservo_en_bloque(reservas, estudiante_codigo, nuevo_inicio, nuevo_fin):
    for r in reservas:
        if r["estudiante_codigo"] != estudiante_codigo:
            continue
        existente_inicio = convertir_a_minutos(r["hora_inicio"])
        existente_fin = convertir_a_minutos(r["hora_fin"])
        if nuevo_inicio < existente_fin and nuevo_fin > existente_inicio:
            return True
    return False


def crear_reserva(salas, reservas, estudiante_codigo, sala_id, hora_inicio, hora_fin, asistentes):
    if sala_id not in salas:
        return {"estado": "RECHAZADA", "mensaje": "La sala solicitada no existe."}

    capacidad_maxima = salas[sala_id]["capacidad"]
    if asistentes > capacidad_maxima:
        return {"estado": "RECHAZADA", "mensaje": "La cantidad de asistentes supera la capacidad de la sala."}

    nuevo_inicio = convertir_a_minutos(hora_inicio)
    nuevo_fin = convertir_a_minutos(hora_fin)

    if _estudiante_ya_reservo_en_bloque(reservas, estudiante_codigo, nuevo_inicio, nuevo_fin):
        return {"estado": "RECHAZADA", "mensaje": "El estudiante ya cuenta con un espacio reservado en ese horario."}

    if _hay_conflicto_horario(reservas, sala_id, nuevo_inicio, nuevo_fin):
        return {"estado": "RECHAZADA", "mensaje": "Cruce de horarios o no se respetan los 15 minutos de desalojo."}

    reservas.append({
        "sala_id": sala_id,
        "estudiante_codigo": estudiante_codigo,
        "hora_inicio": hora_inicio,
        "hora_fin": hora_fin,
    })
    return {"estado": "CONFIRMADA", "mensaje": "Reserva exitosa."}

