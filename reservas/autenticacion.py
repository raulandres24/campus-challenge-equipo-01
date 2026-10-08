"""
reservas/autenticacion.py
=========================
Inicio de sesión: FE → MW → DB del proyecto.

Verifica código, correo y contraseña contra la cuenta que la persona creó al registrarse
(``User`` de Django). **No consulta el padrón**: el padrón solo se usa en el registro
(ver ``reservas/padron.py``).
"""

from __future__ import annotations

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User


class CodigoCorreoBackend(BaseBackend):
    """Autentica con código (username) + correo + contraseña de la base del proyecto."""

    def authenticate(self, request, codigo=None, email=None, password=None, **kwargs):
        if codigo is None or email is None or password is None:
            return None  # no es un intento de este formulario
        usuario = User.objects.filter(username=(codigo or "").strip()).first()
        if usuario is None:
            User().set_password(password)  # mismo costo que un intento real: no revela si el código existe
            return None
        correo_ok = (usuario.email or "").strip().lower() == (email or "").strip().lower()
        if correo_ok and usuario.check_password(password) and usuario.is_active:
            return usuario
        return None

    def get_user(self, user_id):
        return User.objects.filter(pk=user_id, is_active=True).first()
