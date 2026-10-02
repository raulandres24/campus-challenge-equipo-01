"""
proyecto/clases/sala.py
=======================
Funciones simples y aisladas para la consulta y validación de salas contra MongoDB.
"""

from __future__ import annotations

from typing import Optional, Tuple, Union

from ._db import asegurar_django

asegurar_django()

from reservas.models import Sala as SalaModel


def obtener_sala(nombre_o_num: Union[str, int]) -> Optional[SalaModel]:
    """Obtiene una sala de MongoDB buscando por nombre exacto, alias o número.

    Ejemplos de búsqueda:
        - "Sala Alfa" -> Sala Alfa
        - "Alfa" -> Sala Alfa
        - "A" -> Sala A o Sala Alfa
    """
    termino = str(nombre_o_num).strip()
    # 1. Búsqueda exacta por nombre
    sala = SalaModel.objects.filter(nombre__iexact=termino).first()
    if sala:
        return sala

    # 2. Búsqueda con prefijo 'Sala '
    sala = SalaModel.objects.filter(nombre__iexact=f"Sala {termino}").first()
    if sala:
        return sala

    # 3. Búsqueda por contención
    sala = SalaModel.objects.filter(nombre__icontains=termino).first()
    return sala


def validar_sala_habilitada(
    sala_ref: Union[str, int, SalaModel, Sala],
) -> Tuple[bool, str, Optional[SalaModel]]:
    """Valida si una sala existe y se encuentra habilitada (sin mantenimiento) en MongoDB.

    Retorna:
        Tuple[bool, str, Optional[SalaModel]]:
            - bool: True si la sala está habilitada y lista para uso, False en caso contrario.
            - str: Mensaje descriptivo.
            - Optional[SalaModel]: Instancia de la sala o None.
    """
    if isinstance(sala_ref, SalaModel):
        sala = sala_ref
    elif isinstance(sala_ref, Sala):
        sala = obtener_sala(sala_ref.id) or obtener_sala(sala_ref.nombre)
        if sala is None:
            return False, f"La sala '{sala_ref.nombre or sala_ref.id}' no existe en el sistema.", None
    else:
        sala = obtener_sala(sala_ref)

    if sala is None:
        return False, f"La sala solicitada '{sala_ref}' no existe en la base de datos.", None

    if sala.en_mantenimiento:
        return (
            False,
            f"La sala '{sala.nombre}' está en mantenimiento y no puede reservarse.",
            None,
        )

    return True, f"La sala '{sala.nombre}' se encuentra habilitada.", sala


class Sala:
    """Clase liviana de Sala para compatibilidad."""

    def __init__(
        self,
        id_sala: Union[str, int],
        capacidad: int = 10,
        nombre: str = "",
        en_mantenimiento: bool = False,
    ):
        self.id = str(id_sala)
        self.nombre = nombre or str(id_sala)
        self.capacidad = capacidad
        self.en_mantenimiento = en_mantenimiento

    @property
    def disponible(self) -> bool:
        return not self.en_mantenimiento

    def __repr__(self) -> str:
        return f"Sala(id='{self.id}', nombre='{self.nombre}', capacidad={self.capacidad}, mantenimiento={self.en_mantenimiento})"