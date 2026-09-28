from .reserva import Reserva
from .estudiante import Estudiante


class SistemaReservas:
    def __init__(self):
        self.salas = {}
        self.reservas = []

    def agregar_sala(self, sala):
        self.salas[sala.id] = sala

    def crear_reserva(self, estudiante, id_sala, hora_inicio, hora_fin, asistentes):
        if id_sala not in self.salas:
            return {"estado": "RECHAZADA", "mensaje": "La sala solicitada no existe."}

        sala = self.salas[id_sala]
        if asistentes > sala.capacidad:
            return {"estado": "RECHAZADA", "mensaje": "La cantidad de asistentes supera la capacidad de la sala."}

        nueva_reserva = Reserva(sala, estudiante, hora_inicio, hora_fin)

        for r in self.reservas:
            if nueva_reserva.es_del_mismo_estudiante_en_bloque(r):
                return {"estado": "RECHAZADA",
                        "mensaje": "El estudiante ya cuenta con un espacio reservado en ese horario."}
            if nueva_reserva.choca_con(r):
                return {"estado": "RECHAZADA",
                        "mensaje": "Cruce de horarios o no se respetan los 15 minutos de desalojo."}

        self.reservas.append(nueva_reserva)
        return {"estado": "CONFIRMADA", "mensaje": "Reserva exitosa."}

    def consultar_espacios_disponibles(self, hora_inicio, hora_fin, buffer_min=15):
        estudiante_temp = Estudiante(0)
        disponibles = []

        for id_sala, sala in self.salas.items():
            reserva_temp = Reserva(sala, estudiante_temp, hora_inicio, hora_fin)
            if not any(reserva_temp.choca_con(r, buffer_min) for r in self.reservas):
                disponibles.append(sala.id)

        return disponibles

    def cancelar_reserva(self, codigo_estudiante, id_sala):
        for r in self.reservas:
            if r.estudiante.codigo == codigo_estudiante and r.sala.id == id_sala:
                self.reservas.remove(r)
                return {"estado": "EXITO", "mensaje": "Reserva cancelada correctamente."}
        return {"estado": "RECHAZADA", "mensaje": "No se encontró ninguna reserva activa."}