#!/usr/bin/env python
"""
manage.py
=========
Utilidad de línea de comandos de Django para tareas administrativas del proyecto.
"""
import os
import sys


def main():
    """Ejecuta las tareas administrativas de Django."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reservas_upb.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. ¿Está instalado y disponible en el "
            "entorno virtual activo?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

