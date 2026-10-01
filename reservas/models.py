from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Sala(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    capacidad = models.PositiveIntegerField()
    ubicacion = models.CharField(max_length=100, blank=True)
    tiene_proyector = models.BooleanField(default=False)
    tiene_pizarra = models.BooleanField(default=False)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class Reserva(models.Model):
    ESTADO_CONFIRMADA = "CONFIRMADA"
    ESTADO_CANCELADA = "CANCELADA"
    ESTADOS = [
        (ESTADO_CONFIRMADA, "Confirmada"),
        (ESTADO_CANCELADA, "Cancelada"),
    ]

    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name="reservas")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reservas")
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    asistentes = models.PositiveIntegerField()
    estado = models.CharField(max_length=12, choices=ESTADOS, default=ESTADO_CONFIRMADA)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sala} — {self.fecha} {self.hora_inicio}-{self.hora_fin} ({self.usuario})"

    def _choca_con(self, otra, buffer_minutos=15):
        """Misma lógica que proyecto/clases/reserva.py: cruce de horario
        respetando 15 minutos de desalojo entre reservas de la misma sala."""
        if self.sala_id != otra.sala_id or self.fecha != otra.fecha:
            return False
        inicio_a = self._a_minutos(self.hora_inicio) - buffer_minutos
        fin_a = self._a_minutos(self.hora_fin) + buffer_minutos
        inicio_b = self._a_minutos(otra.hora_inicio)
        fin_b = self._a_minutos(otra.hora_fin)
        return inicio_a < fin_b and fin_a > inicio_b

    @staticmethod
    def _a_minutos(hora):
        return hora.hour * 60 + hora.minute

    def clean(self):
        if self.hora_fin <= self.hora_inicio:
            raise ValidationError("La hora de fin debe ser posterior a la hora de inicio.")

        if self.sala_id and self.asistentes and self.asistentes > self.sala.capacidad:
            raise ValidationError("La cantidad de asistentes supera la capacidad de la sala.")

        activas = Reserva.objects.filter(
            sala=self.sala, fecha=self.fecha, estado=self.ESTADO_CONFIRMADA
        ).exclude(pk=self.pk)
        for otra in activas:
            if self._choca_con(otra):
                raise ValidationError("Cruce de horario o no se respetan los 15 minutos de desalojo.")

        mismo_bloque = Reserva.objects.filter(
            usuario=self.usuario, fecha=self.fecha, estado=self.ESTADO_CONFIRMADA
        ).exclude(pk=self.pk)
        for otra in mismo_bloque:
            inicio_a, fin_a = self._a_minutos(self.hora_inicio), self._a_minutos(self.hora_fin)
            inicio_b, fin_b = self._a_minutos(otra.hora_inicio), self._a_minutos(otra.hora_fin)
            if inicio_a < fin_b and fin_a > inicio_b:
                raise ValidationError("Ya cuentas con una reserva activa en ese horario.")