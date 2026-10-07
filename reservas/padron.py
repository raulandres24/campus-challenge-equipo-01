"""
reservas/padron.py
==================
Padrón SIMULADO de la UPB (la "DB estática" de la pizarra del docente).

    FE → MW → [DB estática: padrón] → DB del proyecto

- El padrón es un archivo JSON de solo lectura: ``datos/padron_upb.json``
  (19 personas ficticias: estudiantes de pregrado, postgrado y doctorado, un docente
  y tres administradores). El sistema nunca lo modifica.
- Si existe ``datos/padron_local.json`` (excluido de git), se usa ese.
  Sirve para cargar otros datos sin subirlos al repositorio público.
- **Un solo inicio de sesión** para todos: código (5 dígitos) + correo institucional +
  contraseña. El rol sale del padrón (``estudiante``, ``docente`` o ``admin``); no hay
  pantallas distintas.
- La contraseña no se guarda: el padrón solo tiene su *hash* (``password_hash``, mismo
  formato que usa Django). Para generar uno:
  ``python manage.py shell -c "from django.contrib.auth.hashers import make_password; print(make_password('clave'))"``
- Si la persona figura, está activa y la contraseña coincide, se crea o actualiza su
  ``User`` de Django (username = código) y, si es estudiante, su ``Estudiante`` con los
  datos del padrón (nivel académico y matrícula vigente: fuente del dato de RES-RF-05).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
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
        datos = json.load(archivo)
    return datos["personas"]


def buscar_en_padron(codigo: str, email: str, padron: Optional[list[dict]] = None) -> Optional[dict]:
    """Devuelve la persona del padrón con ese código Y ese correo, o None.

    El código y el correo se comparan sin distinguir mayúsculas.
    """
    codigo = (codigo or "").strip().upper()
    email = (email or "").strip().lower()
    if not codigo or not email:
        return None
    for persona in padron if padron is not None else cargar_padron():
        if persona["codigo"].upper() == codigo and persona["email"].lower() == email:
            return persona
    return None


def buscar_por_codigo(codigo: str, padron: Optional[list[dict]] = None) -> Optional[dict]:
    """Persona del padrón con ese código (para saber su rol), o None."""
    codigo = (codigo or "").strip().upper()
    if not codigo:
        return None
    for persona in padron if padron is not None else cargar_padron():
        if persona["codigo"].upper() == codigo:
            return persona
    return None


def verificar_credenciales(
    codigo: str, email: str, password: str, padron: Optional[list[dict]] = None
) -> Optional[dict]:
    """Persona del padrón si el código, el correo Y la contraseña coinciden; si no, None.

    No mira si está activa: eso lo decide quien llama, para poder avisarle solo a quien
    ya demostró ser esa persona (no se revela a un desconocido si un código existe).
    """
    persona = buscar_en_padron(codigo, email, padron)
    if persona is None:
        return None
    if not check_password(password or "", persona.get("password_hash", "")):
        return None
    return persona


ROLES_CON_PODERES = {"docente", "admin"}


def sincronizar_desde_padron(persona: dict) -> User:
    """Crea o actualiza el User de Django (y el Estudiante, si lo es) con los datos del padrón."""
    if persona.get("rol", "estudiante") == "estudiante":
        estudiante, _ = Estudiante.objects.get_or_create(
            codigo_estudiante=persona["codigo"],
            defaults={"nombres": persona["nombres"], "apellidos": persona["apellidos"]},
        )
        estudiante.nombres = persona["nombres"]
        estudiante.apellidos = persona["apellidos"]
        estudiante.esta_activo = bool(persona["activo"])
        estudiante.matricula_pagada = bool(persona["matricula_vigente"])
        estudiante.nivel = persona.get("nivel") or Estudiante.NIVEL_PREGRADO
        estudiante.save()

    usuario, _ = User.objects.get_or_create(username=persona["codigo"])
    usuario.first_name = persona["nombres"]
    usuario.last_name = persona["apellidos"]
    usuario.email = persona["email"]
    usuario.is_active = bool(persona["activo"])
    # Docentes y administradores gestionan salas y reservas ajenas (permisos.py → is_staff).
    # Nadie recibe is_superuser desde el padrón.
    usuario.is_staff = persona.get("rol") in ROLES_CON_PODERES
    usuario.is_superuser = False
    usuario.password = persona.get("password_hash") or ""
    if not usuario.password:
        usuario.set_unusable_password()
    usuario.save()
    return usuario


class PadronBackend(BaseBackend):
    """Backend de autenticación de Django: código + correo + contraseña contra el padrón.

    Es el único acceso de la pantalla de inicio de sesión. ``ModelBackend`` se conserva
    solo para el sitio ``/admin/`` de Django (superusuarios creados con ``createsuperuser``).
    """

    def authenticate(self, request, codigo=None, email=None, password=None, **kwargs):
        if codigo is None or email is None or password is None:
            return None  # no es un intento de login por padrón
        persona = verificar_credenciales(codigo, email, password)
        if persona is None or not persona["activo"]:
            return None
        return sincronizar_desde_padron(persona)

    def get_user(self, user_id):
        return User.objects.filter(pk=user_id, is_active=True).first()
