"""
proyecto/clases package
=======================
Exporta todas las funciones simples, aisladas y de orquestación del sistema de reservas.
"""

from .estudiante import (
    Estudiante,
    obtener_estudiante,
    validar_estudiante_habilitado,
)
from .horarios import (
    BUFFER_DESALOJO_MINUTOS,
    convertir_a_minutos,
    hay_choque_con_buffer,
    hay_solapamiento_simple,
    minutos_a_time,
    parsear_horas,
    validar_rango_horario,
)
from .reserva import (
    Reserva,
    cancelar_reserva_en_mongo,
    consultar_salas_disponibles_dia,
    guardar_reserva_mongo,
    normalizar_fecha,
    revisar_choque_horario_dia,
    revisar_reserva_estudiante_en_horario,
)
from .sala import (
    Sala,
    obtener_sala,
    validar_sala_habilitada,
)
from .sistema_reservas import (
    SistemaReservas,
    cancelar_reserva,
    consultar_espacios_disponibles,
    reservar_si_es_posible,
    reservarSiesPosible,
)

__all__ = [
    # Horarios
    "BUFFER_DESALOJO_MINUTOS",
    "convertir_a_minutos",
    "minutos_a_time",
    "validar_rango_horario",
    "hay_choque_con_buffer",
    "hay_solapamiento_simple",
    "parsear_horas",
    # Estudiantes
    "Estudiante",
    "obtener_estudiante",
    "validar_estudiante_habilitado",
    # Salas
    "Sala",
    "obtener_sala",
    "validar_sala_habilitada",
    # Reservas y BD
    "Reserva",
    "normalizar_fecha",
    "revisar_choque_horario_dia",
    "revisar_reserva_estudiante_en_horario",
    "guardar_reserva_mongo",
    "cancelar_reserva_en_mongo",
    "consultar_salas_disponibles_dia",
    # Orquestación / API
    "reservar_si_es_posible",
    "reservarSiesPosible",
    "consultar_espacios_disponibles",
    "cancelar_reserva",
    "SistemaReservas",
]
