"""Modificacion de reservas existentes (PB-04)."""
from proyecto.reglas import (
    convertir_a_minutos,
    _hay_conflicto_horario,
    _estudiante_ya_reservo_en_bloque,
)


def _rechazo(mensaje):
    return {"estado": "RECHAZADA", "mensaje": mensaje}


def modificar_reserva(
    salas,
    reservas,
    estudiante_codigo,
    sala_id,
    hora_inicio_actual,
    nueva_hora_inicio=None,
    nueva_hora_fin=None,
    nuevos_asistentes=None,
):
    """Cambia horario y/o asistentes de una reserva existente.

    La reserva se identifica por (estudiante, sala, hora de inicio actual).
    Regla clave del encargo: si el cambio es invalido, la reserva original
    queda EXACTAMENTE como estaba.
    """
    # 1. Buscar la reserva a modificar.
    indice = None
    for i, r in enumerate(reservas):
        if (
            r["estudiante_codigo"] == estudiante_codigo
            and r["sala_id"] == sala_id
            and r["hora_inicio"] == hora_inicio_actual
        ):
            indice = i
            break
    if indice is None:
        return _rechazo("No existe una reserva con esos datos.")

    if sala_id not in salas:
        return _rechazo("La sala solicitada no existe.")

    actual = reservas[indice]

    # 2. Armar los valores candidatos (lo no indicado se conserva).
    hora_inicio = nueva_hora_inicio or actual["hora_inicio"]
    hora_fin = nueva_hora_fin or actual["hora_fin"]
    asistentes = nuevos_asistentes if nuevos_asistentes is not None else actual.get("asistentes")

    inicio = convertir_a_minutos(hora_inicio)
    fin = convertir_a_minutos(hora_fin)

    # 3. Validar TODO antes de tocar la lista.
    if fin <= inicio:
        return _rechazo("La hora de fin debe ser posterior a la hora de inicio.")

    if asistentes is not None and asistentes > salas[sala_id]["capacidad"]:
        return _rechazo("La cantidad de asistentes supera la capacidad de la sala.")

    # La reserva no debe chocar consigo misma: se compara contra las demas.
    otras = reservas[:indice] + reservas[indice + 1:]

    if _estudiante_ya_reservo_en_bloque(otras, estudiante_codigo, inicio, fin):
        return _rechazo("El estudiante ya cuenta con un espacio reservado en ese horario.")

    if _hay_conflicto_horario(otras, sala_id, inicio, fin):
        return _rechazo("Cruce de horarios o no se respetan los 15 minutos de desalojo.")

    # 4. Recien ahora se reemplaza.
    nueva = {**actual, "hora_inicio": hora_inicio, "hora_fin": hora_fin}
    if asistentes is not None:
        nueva["asistentes"] = asistentes
    reservas[indice] = nueva
    return {"estado": "MODIFICADA", "mensaje": "Reserva modificada correctamente."}
