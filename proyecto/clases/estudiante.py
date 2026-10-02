"""
proyecto/clases/estudiante.py
=============================
Funciones simples y aisladas para la consulta y validación de estudiantes contra MongoDB.
"""

from __future__ import annotations

from typing import Optional, Tuple, Union

from ._db import asegurar_django

asegurar_django()

from reservas.models import Estudiante as EstudianteModel


def obtener_estudiante(codigo_estudiante: Union[str, int]) -> Optional[EstudianteModel]:
    """Obtiene un estudiante de MongoDB por su código.

    Retorna la instancia de EstudianteModel o None si no existe.
    """
    codigo_str = str(codigo_estudiante).strip()
    return EstudianteModel.objects.filter(codigo_estudiante=codigo_str).first()


def validar_estudiante_habilitado(
    codigo_o_estudiante: Union[str, int, EstudianteModel, Estudiante],
) -> Tuple[bool, str, Optional[EstudianteModel]]:
    """Valida si un estudiante existe, está activo y tiene su matrícula al día en MongoDB.

    Retorna:
        Tuple[bool, str, Optional[EstudianteModel]]:
            - bool: True si está habilitado para reservar, False en caso contrario.
            - str: Mensaje descriptivo del resultado.
            - Optional[EstudianteModel]: Instancia del estudiante si es válido, o None.
    """
    if isinstance(codigo_o_estudiante, EstudianteModel):
        estudiante = codigo_o_estudiante
    elif isinstance(codigo_o_estudiante, Estudiante):
        estudiante = obtener_estudiante(codigo_o_estudiante.codigo)
        if estudiante is None:
            return (
                False,
                f"El estudiante con código '{codigo_o_estudiante.codigo}' no está registrado en el sistema.",
                None,
            )
    else:
        estudiante = obtener_estudiante(codigo_o_estudiante)

    if estudiante is None:
        return (
            False,
            f"El estudiante con código '{codigo_o_estudiante}' no está registrado en el sistema.",
            None,
        )

    if not estudiante.esta_activo:
        return (
            False,
            f"El estudiante '{estudiante}' no está activo en el sistema.",
            None,
        )

    if not estudiante.matricula_pagada:
        return (
            False,
            f"El estudiante '{estudiante}' no tiene la matrícula pagada.",
            None,
        )

    return True, "Estudiante habilitado para realizar reservas.", estudiante


class Estudiante:
    """Clase liviana de Estudiante para compatibilidad."""

    def __init__(
        self,
        codigo: Union[str, int],
        nombres: str = "",
        apellidos: str = "",
        esta_activo: bool = True,
        matricula_pagada: bool = True,
    ):
        self.codigo = str(codigo)
        self.nombres = nombres
        self.apellidos = apellidos
        self.esta_activo = esta_activo
        self.matricula_pagada = matricula_pagada

    @property
    def puede_reservar(self) -> bool:
        return self.esta_activo and self.matricula_pagada

    def __repr__(self) -> str:
        return f"Estudiante(codigo='{self.codigo}', activo={self.esta_activo}, matricula={self.matricula_pagada})"