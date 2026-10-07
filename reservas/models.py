"""
reservas/models.py
==================
Definición de modelos de base de datos para MongoDB usando django-mongodb-backend.
Incluye:
  - Estudiante: solicitante y beneficiario de la reserva.
  - Sala: espacio físico reservable en el campus UPB.
  - Reserva: registro de ocupación con soporte para buffer de 15 minutos de desalojo.
"""

from django.core.exceptions import ValidationError
from django.db import models


# ---------------------------------------------------------------------------
# Modelo: Estudiante
# ---------------------------------------------------------------------------

class Estudiante(models.Model):
    """Estudiante universitario solicitante en el sistema de reservas UPB."""

    NIVEL_PREGRADO = "pregrado"
    NIVEL_POSTGRADO = "postgrado"
    NIVEL_DOCTORADO = "doctorado"
    NIVELES = [
        (NIVEL_PREGRADO, "Pregrado"),
        (NIVEL_POSTGRADO, "Postgrado"),
        (NIVEL_DOCTORADO, "Doctorado"),
    ]

    codigo_estudiante = models.CharField(max_length=20, unique=True, verbose_name="Código de Estudiante")
    nombres = models.CharField(max_length=100, verbose_name="Nombres")
    apellidos = models.CharField(max_length=100, verbose_name="Apellidos")
    esta_activo = models.BooleanField(default=True, verbose_name="¿Está Activo?")
    matricula_pagada = models.BooleanField(default=False, verbose_name="¿Matrícula Pagada?")
    nivel = models.CharField(
        max_length=10,
        choices=NIVELES,
        default=NIVEL_PREGRADO,
        verbose_name="Nivel académico",
        help_text="Define qué salas puede reservar (ver reservas/niveles.py).",
    )

    class Meta:
        ordering = ["apellidos", "nombres"]
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"

    def __str__(self) -> str:
        return f"{self.nombres} {self.apellidos} ({self.codigo_estudiante})"

    @property
    def puede_reservar(self) -> bool:
        """Indica si el estudiante se encuentra habilitado (activo y con matrícula pagada)."""
        return self.esta_activo and self.matricula_pagada


# ---------------------------------------------------------------------------
# Modelo: Sala
# ---------------------------------------------------------------------------

class Sala(models.Model):
    """Espacio físico de estudio o reunión en el campus UPB."""

    nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre de la Sala")
    en_mantenimiento = models.BooleanField(
        default=False,
        verbose_name="¿En Mantenimiento?",
        help_text="Indica si la sala se encuentra temporalmente fuera de servicio.",
    )
    exclusiva_posgrado = models.BooleanField(
        default=False,
        verbose_name="¿Exclusiva de postgrado y doctorado?",
        help_text="Si está marcada, solo la reservan estudiantes de postgrado o doctorado (salas A y E).",
    )

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Sala"
        verbose_name_plural = "Salas"

    def __str__(self) -> str:
        sufijo = " [EN MANTENIMIENTO]" if self.en_mantenimiento else ""
        return f"{self.nombre}{sufijo}"

    @property
    def disponible(self) -> bool:
        """Indica si la sala está habilitada para ser reservada."""
        return not self.en_mantenimiento


# ---------------------------------------------------------------------------
# Modelo: Reserva
# ---------------------------------------------------------------------------

class Reserva(models.Model):
    """Registro histórico y activo de reserva de una sala en MongoDB."""

    ESTADO_CONFIRMADA = "CONFIRMADA"
    ESTADO_CANCELADA = "CANCELADA"
    ESTADOS = [
        (ESTADO_CONFIRMADA, "Confirmada"),
        (ESTADO_CANCELADA, "Cancelada"),
    ]

    BUFFER_MINUTOS = 15  # Margen obligatorio de desalojo entre reservas consecutivas

    estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.CASCADE,
        related_name="reservas",
        verbose_name="Estudiante",
    )
    sala = models.ForeignKey(
        Sala,
        on_delete=models.CASCADE,
        related_name="reservas",
        verbose_name="Sala",
    )
    fecha = models.DateField(verbose_name="Fecha de la Reserva")
    hora_inicio = models.TimeField(verbose_name="Hora de Inicio")
    hora_fin = models.TimeField(verbose_name="Hora de Fin")
    estado = models.CharField(
        max_length=12,
        choices=ESTADOS,
        default=ESTADO_CONFIRMADA,
        verbose_name="Estado de la Reserva",
    )
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora de Creación")

    class Meta:
        ordering = ["fecha", "hora_inicio"]
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"

    def __str__(self) -> str:
        return (
            f"{self.sala} - {self.fecha} "
            f"{self.hora_inicio:%H:%M}-{self.hora_fin:%H:%M} "
            f"({self.estudiante})"
        )

    @staticmethod
    def _a_minutos(hora) -> int:
        """Convierte un objeto datetime.time a minutos desde medianoche."""
        return hora.hour * 60 + hora.minute

    def _rango_bloqueado(self) -> tuple[int, int]:
        """Calcula el intervalo de minutos bloqueados considerando el buffer de desalojo."""
        inicio = self._a_minutos(self.hora_inicio) - self.BUFFER_MINUTOS
        fin = self._a_minutos(self.hora_fin) + self.BUFFER_MINUTOS
        return inicio, fin

    def choca_con(self, otra: 'Reserva') -> bool:
        """Verifica si esta reserva colisiona con otra en la misma sala y fecha considerando el buffer."""
        if self.sala_id != otra.sala_id or self.fecha != otra.fecha:
            return False
        inicio_a, fin_a = self._rango_bloqueado()
        inicio_b = self._a_minutos(otra.hora_inicio)
        fin_b = self._a_minutos(otra.hora_fin)
        return inicio_a < fin_b and fin_a > inicio_b

    def solapa_estudiante(self, otra: 'Reserva') -> bool:
        """Verifica si el mismo estudiante intenta reservar dos salas en el mismo intervalo de tiempo."""
        if self.estudiante_id != otra.estudiante_id or self.fecha != otra.fecha:
            return False
        inicio_a = self._a_minutos(self.hora_inicio)
        fin_a = self._a_minutos(self.hora_fin)
        inicio_b = self._a_minutos(otra.hora_inicio)
        fin_b = self._a_minutos(otra.hora_fin)
        return inicio_a < fin_b and fin_a > inicio_b

    def clean(self):
        """Valida que la hora de fin sea estrictamente posterior a la de inicio."""
        if self.hora_fin <= self.hora_inicio:
            raise ValidationError("La hora de fin debe ser posterior a la hora de inicio.")