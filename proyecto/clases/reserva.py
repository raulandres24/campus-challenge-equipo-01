class Reserva:
    def __init__(self, sala, estudiante, hora_inicio, hora_fin):
        self.sala = sala
        self.estudiante = estudiante
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.min_inicio = self._convertir_a_minutos(hora_inicio)
        self.min_fin = self._convertir_a_minutos(hora_fin)

    def _convertir_a_minutos(self, hora_texto):
        partes = hora_texto.split(":")
        return int(partes[0]) * 60 + int(partes[1])

    def choca_con(self, otra_reserva, buffer_min=15):
        if self.sala.id != otra_reserva.sala.id:
            return False
        if self.min_inicio < (otra_reserva.min_fin + buffer_min) and self.min_fin > (otra_reserva.min_inicio - buffer_min):
            return True
        return False

    def es_del_mismo_estudiante_en_bloque(self, otra_reserva):
        if self.estudiante.codigo != otra_reserva.estudiante.codigo:
            return False
        if self.min_inicio < otra_reserva.min_fin and self.min_fin > otra_reserva.min_inicio:
            return True
        return False