from django.core.exceptions import ValidationError
from django.db import models


# ---------------------------------------------------------------------------
# Estudiante
# ---------------------------------------------------------------------------

class Estudiante(models.Model):
    """Solicitante del sistema de reservas de salas UPB."""

    codigo_estudiante = models.CharField(max_length=20, unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    esta_activo = models.BooleanField(default=True)
    matricula_pagada = models.BooleanField(default=False)

    class Meta:
        ordering = ["apellidos", "nombres"]
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.codigo_estudiante})"

    @property
    def puede_reservar(self) -> bool:
        """True si el estudiante esta activo y con matricula al dia."""
        return self.esta_activo and self.matricula_pagada


# ---------------------------------------------------------------------------
# Sala
# ---------------------------------------------------------------------------

class Sala(models.Model):
    """Espacio fisico reservable dentro del campus UPB."""

    nombre = models.CharField(max_length=50, unique=True)
    en_mantenimiento = models.BooleanField(
        default=False,
        help_text="Marca la sala como no disponible temporalmente.",
    )

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Sala"
        verbose_name_plural = "Salas"

    def __str__(self):
        sufijo = " [EN MANTENIMIENTO]" if self.en_mantenimiento else ""
        return f"{self.nombre}{sufijo}"

    @property
    def disponible(self) -> bool:
        """Disponible cuando no esta en mantenimiento."""
        return not self.en_mantenimiento


# ---------------------------------------------------------------------------
# Reserva
# ---------------------------------------------------------------------------

class Reserva(models.Model):
    """Registro de la ocupacion de una sala por un estudiante."""

    ESTADO_CONFIRMADA = "CONFIRMADA"
    ESTADO_CANCELADA = "CANCELADA"
    ESTADOS = [
        (ESTADO_CONFIRMADA, "Confirmada"),
        (ESTADO_CANCELADA, "Cancelada"),
    ]

    BUFFER_MINUTOS = 15  # Intervalo de desalojo acordado en sesion04.md

    estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.CASCADE,
        related_name="reservas",
    )
    sala = models.ForeignKey(
        Sala,
        on_delete=models.CASCADE,
        related_name="reservas",
    )
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    estado = models.CharField(
        max_length=12,
        choices=ESTADOS,
        default=ESTADO_CONFIRMADA,
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["fecha", "hora_inicio"]
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"

    def __str__(self):
        return (
            f"{self.sala} - {self.fecha} "
            f"{self.hora_inicio:%H:%M}-{self.hora_fin:%H:%M} "
            f"({self.estudiante})"
        )

    @staticmethod
    def _a_minutos(hora) -> int:
        """Convierte un objeto time a minutos desde medianoche."""
        return hora.hour * 60 + hora.minute

    def _rango_bloqueado(self) -> tuple:
        """Rango de bloqueo de esta reserva extendido con el buffer."""
        inicio = self._a_minutos(self.hora_inicio) - self.BUFFER_MINUTOS
        fin = self._a_minutos(self.hora_fin) + self.BUFFER_MINUTOS
        return inicio, fin

    def choca_con(self, otra) -> bool:
        """True si esta reserva solapa (con buffer) con otra en la misma sala/fecha."""
        if self.sala_id != otra.sala_id or self.fecha != otra.fecha:
            return False
        inicio_a, fin_a = self._rango_bloqueado()
        inicio_b = self._a_minutos(otra.hora_inicio)
        fin_b = self._a_minutos(otra.hora_fin)
        return inicio_a < fin_b and fin_a > inicio_b

    def solapa_estudiante(self, otra) -> bool:
        """True si el mismo estudiante tiene otra reserva solapada en tiempo."""
        if self.estudiante_id != otra.estudiante_id or self.fecha != otra.fecha:
            return False
        inicio_a = self._a_minutos(self.hora_inicio)
        fin_a = self._a_minutos(self.hora_fin)
        inicio_b = self._a_minutos(otra.hora_inicio)
        fin_b = self._a_minutos(otra.hora_fin)
        return inicio_a < fin_b and fin_a > inicio_b

    def clean(self):
        if self.hora_fin <= self.hora_inicio:
            raise ValidationError("La hora de fin debe ser posterior a la hora de inicio.")