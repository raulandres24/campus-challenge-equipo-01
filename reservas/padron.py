"""
reservas/padron.py
==================
Padrón SIMULADO de la UPB (la "DB estática" de la pizarra del docente).

Recorrido que explicó el docente (07/10/2026): el padrón se consulta **solo al registrarse**.

    REGISTRO:       FE → MW → [DB estática: padrón] → DB del proyecto
    INICIAR SESIÓN: FE → MW → DB del proyecto        (la persona ya está registrada)

- El padrón es un archivo JSON de solo lectura: ``datos/padron_upb.json``
  (19 personas ficticias: estudiantes de pregrado, postgrado y doctorado, un docente
  y tres administradores). El sistema nunca lo modifica.
- Si existe ``datos/padron_local.json`` (excluido de git), se usa ese.
  Sirve para cargar otros datos sin subirlos al repositorio público.
- Al registrarse, la persona escribe su código (5 dígitos) y su correo institucional.
  Si figuran juntos en el padrón y está activa, elige su contraseña y se crea su cuenta en
  la base del proyecto: un ``User`` de Django (username = código) y, si es estudiante, su
  ``Estudiante`` con el nivel académico y la matrícula vigente del padrón.
- El padrón no guarda contraseñas. Cada persona elige la suya al registrarse y Django
  guarda solo su *hash* en la base del proyecto.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from django.conf import settings
from django.contrib.auth.models import User

from .models import Estudiante

CARPETA_DATOS = Path(settings.BASE_DIR) / "datos"

# Docentes y administradores gestionan salas y reservas ajenas (permisos.py → is_staff).
ROLES_CON_PODERES = {"docente", "admin"}


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


def registrar_desde_padron(persona: dict, password: str) -> User:
    """Crea (o rehace) la cuenta de una persona del padrón en la base del proyecto.

    ``password`` se guarda con hash de Django. La vista de registro es quien comprueba que
    la persona esté activa y que la cuenta no exista; esta función no lo hace, para que
    ``poblar_bd`` pueda recrear las cuentas de demostración.
    """
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
    usuario.is_staff = persona.get("rol") in ROLES_CON_PODERES
    usuario.is_superuser = False  # nadie recibe superusuario desde el padrón
    usuario.set_password(password)
    usuario.save()
    return usuario
