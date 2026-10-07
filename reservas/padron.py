"""
reservas/padron.py
==================
Padrón SIMULADO de la UPB (la "DB estática" de la pizarra del docente).

    FE → MW → [DB estática: padrón] → DB del proyecto

- El padrón es un archivo JSON de solo lectura: ``datos/padron_upb.json``
  (15 estudiantes ficticios). El sistema nunca lo modifica.
- Si existe ``datos/padron_local.json`` (excluido de git), se usa ese.
  Sirve para cargar otros datos sin subirlos al repositorio público.
- Al iniciar sesión, un estudiante escribe su código y su correo institucional.
  Si figura en el padrón y está activo, se crea o actualiza su ``User`` de Django
  (username = código) y su ``Estudiante`` con los datos del padrón. Así:
    * el usuario queda enlazado a su código de estudiante (dueño de sus reservas);
    * la matrícula vigente sale del padrón (fuente del dato de RES-RF-05).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User

from .models import Estudiante

CARPETA_DATOS = Path(settings.BASE_DIR) / "datos"


def ruta_padron() -> Path:
    """Archivo del padrón que se usa: el local si existe, si no el ficticio del repositorio."""
    local = CARPETA_DATOS / "padron_local.json"
    return local if local.exists() else CARPETA_DATOS / "padron_upb.json"


def cargar_padron(ruta: Optional[Path] = None) -> list[dict]:
    """Lee el padrón ("JSON query" de la pizarra). Solo lectura."""
    with open(ruta or ruta_padron(), encoding="utf-8") as archivo:
        return json.load(archivo)["estudiantes"]


def buscar_en_padron(codigo: str, email: str, padron: Optional[list[dict]] = None) -> Optional[dict]:
    """Devuelve la persona del padrón con ese código Y ese correo, o None.

    El código se compara sin distinguir mayúsculas; el correo también.
    """
    codigo = (codigo or "").strip().upper()
    email = (email or "").strip().lower()
    if not codigo or not email:
        return None
    for persona in padron if padron is not None else cargar_padron():
        if persona["codigo"].upper() == codigo and persona["email"].lower() == email:
            return persona
    return None


def sincronizar_desde_padron(persona: dict) -> User:
    """Crea o actualiza el Estudiante y el User de Django con los datos del padrón."""
    estudiante, _ = Estudiante.objects.get_or_create(
        codigo_estudiante=persona["codigo"],
        defaults={"nombres": persona["nombres"], "apellidos": persona["apellidos"]},
    )
    estudiante.nombres = persona["nombres"]
    estudiante.apellidos = persona["apellidos"]
    estudiante.esta_activo = bool(persona["activo"])
    estudiante.matricula_pagada = bool(persona["matricula_vigente"])
    estudiante.save()

    usuario, creado = User.objects.get_or_create(username=persona["codigo"])
    usuario.first_name = persona["nombres"]
    usuario.last_name = persona["apellidos"]
    usuario.email = persona["email"]
    usuario.is_active = bool(persona["activo"])
    if creado:
        usuario.set_unusable_password()  # el estudiante entra por el padrón, no con contraseña
    usuario.save()
    return usuario


class PadronBackend(BaseBackend):
    """Backend de autenticación de Django para estudiantes: código + correo contra el padrón.

    Los administradores siguen entrando con usuario y contraseña (ModelBackend).
    """

    def authenticate(self, request, codigo=None, email=None, **kwargs):
        if codigo is None or email is None:
            return None  # no es un intento de login por padrón
        persona = buscar_en_padron(codigo, email)
        if persona is None or not persona["activo"]:
            return None
        return sincronizar_desde_padron(persona)

    def get_user(self, user_id):
        return User.objects.filter(pk=user_id, is_active=True).first()
