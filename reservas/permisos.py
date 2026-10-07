"""
reservas/permisos.py
====================
Control de roles y poderes especiales para el sistema de reservas UPB.
Los usuarios con poderes especiales (Sergio Barrientos, Hugo Zúñiga, Raúl Vaca, Alejandro Párraga y admin)
tienen permisos avanzados para gestionar salas, mantenimiento y cancelar cualquier reserva.
"""

from __future__ import annotations

from typing import Dict, Any

# Usuarios con poderes especiales designados por el sistema
USUARIOS_CON_PODERES = {
    "admin",
    "sbarrientos",
    "sergio.barrientos",
    "hzuniga",
    "hugo.zuniga",
    "rvaca",
    "raul.vaca",
    "aparraga",
    "alejandro.parraga",
}


def tiene_poderes_especiales(user) -> bool:
    """Retorna True si el usuario autenticado tiene poderes especiales de administración."""
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True
    return user.username.lower() in USUARIOS_CON_PODERES


def es_duenio_de_reserva(user, reserva) -> bool:
    """True si el usuario autenticado es el estudiante dueño de la reserva.

    Hoy el ``User`` de Django y el ``Estudiante`` no están enlazados, así que
    se comparan nombres y apellidos (igual que en la vista ``inicio``), pero
    de forma exacta y exigiendo que no estén vacíos. Antes se usaba
    ``first_name in nombres``, y ``"" in "Lucía"`` es True: un usuario sin
    nombre pasaba como dueño de cualquier reserva.

    Cuando se enlace el login con el padrón (código de estudiante), esta es la
    única función que hay que cambiar.
    """
    if not user or not user.is_authenticated:
        return False
    nombre = (user.first_name or "").strip().lower()
    apellido = (user.last_name or "").strip().lower()
    if not nombre or not apellido:
        return False
    estudiante = reserva.estudiante
    return (
        estudiante.nombres.strip().lower() == nombre
        and estudiante.apellidos.strip().lower() == apellido
    )


def obtener_info_usuario(user) -> Dict[str, Any]:
    """Retorna un diccionario con los detalles de perfil, rol y poderes del usuario."""
    if not user or not user.is_authenticated:
        return {
            "autenticado": False,
            "username": "invitado",
            "nombre_completo": "Invitado",
            "tiene_poderes": False,
            "rol": "Invitado",
            "insignia": "VISITANTE",
        }

    es_admin = tiene_poderes_especiales(user)
    nombre = f"{user.first_name} {user.last_name}".strip() or user.username

    # Títulos personalizados para el equipo de honor
    if user.username.lower() in {"sbarrientos", "sergio.barrientos"}:
        rol = "Docente / Director"
        insignia = "👑 INGENIERO DOCENTE"
    elif user.username.lower() in {"hzuniga", "hugo.zuniga"}:
        rol = "Administrador Principal"
        insignia = "👑 ADMIN HUGO"
    elif user.username.lower() in {"rvaca", "raul.vaca"}:
        rol = "Administrador"
        insignia = "👑 ADMIN RAÚL"
    elif user.username.lower() in {"aparraga", "alejandro.parraga"}:
        rol = "Administrador"
        insignia = "👑 ADMIN ALEJANDRO"
    elif es_admin:
        rol = "Superusuario"
        insignia = "👑 SUPERADMIN"
    else:
        rol = "Estudiante Regular"
        insignia = "🎓 ESTUDIANTE UPB"

    return {
        "autenticado": True,
        "username": user.username,
        "nombre_completo": nombre,
        "email": user.email,
        "tiene_poderes": es_admin,
        "rol": rol,
        "insignia": insignia,
    }
