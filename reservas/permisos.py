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


def estudiante_del_usuario(user):
    """Estudiante vinculado al usuario que inició sesión, o None.

    1. Usuarios que entraron por el padrón: su ``username`` es su código de estudiante.
    2. Usuarios antiguos de ``poblar_bd`` (por ejemplo ``lucia.mendez``): nombre y apellido
       exactos y no vacíos. Antes se usaba ``first_name in nombres`` y ``"" in "Lucía"``
       es True: un usuario sin nombre pasaba como cualquier estudiante.
    """
    from .models import Estudiante  # import local: evita ciclos al cargar la app

    if not user or not user.is_authenticated:
        return None
    por_codigo = Estudiante.objects.filter(codigo_estudiante__iexact=user.username).first()
    if por_codigo:
        return por_codigo
    nombre = (user.first_name or "").strip()
    apellido = (user.last_name or "").strip()
    if not nombre or not apellido:
        return None
    return Estudiante.objects.filter(nombres__iexact=nombre, apellidos__iexact=apellido).first()


def es_duenio_de_reserva(user, reserva) -> bool:
    """True si el usuario autenticado es el estudiante dueño de la reserva.

    Primero por código (usuarios del padrón: username = código); si no, por nombre y
    apellido exactos y no vacíos (usuarios antiguos de poblar_bd).
    """
    if not user or not user.is_authenticated:
        return False
    estudiante = reserva.estudiante
    if (user.username or "").strip().upper() == estudiante.codigo_estudiante.strip().upper():
        return True
    nombre = (user.first_name or "").strip().lower()
    apellido = (user.last_name or "").strip().lower()
    if not nombre or not apellido:
        return False
    return (
        estudiante.nombres.strip().lower() == nombre
        and estudiante.apellidos.strip().lower() == apellido
    )


def _persona_del_padron(user):
    """Persona del padrón cuyo código es el username del usuario, o None (también si falta el archivo)."""
    from .padron import buscar_por_codigo  # import local: padron importa los modelos

    try:
        return buscar_por_codigo(user.username)
    except (OSError, KeyError, ValueError):
        return None


def _rol_e_insignia_del_padron(persona):
    """Rol e insignia para mostrar, según el rol y el nivel que dice el padrón."""
    rol = persona.get("rol", "estudiante")
    if rol == "docente":
        return "Docente", "👑 DOCENTE"
    if rol == "admin":
        return "Administrador", "👑 ADMIN"
    nivel = persona.get("nivel") or "pregrado"
    etiquetas = {"pregrado": "🎓 ESTUDIANTE UPB", "postgrado": "🎓 POSTGRADO", "doctorado": "🎓 DOCTORADO"}
    return f"Estudiante de {nivel}", etiquetas.get(nivel, "🎓 ESTUDIANTE UPB")


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

    persona = _persona_del_padron(user)

    # Títulos personalizados para el equipo de honor
    if persona is not None:
        rol, insignia = _rol_e_insignia_del_padron(persona)
    elif user.username.lower() in {"sbarrientos", "sergio.barrientos"}:
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
