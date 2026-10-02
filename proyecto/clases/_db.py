"""
proyecto/clases/_db.py
======================
Garantiza la inicialización de Django y conexión a MongoDB para las funciones de negocio.
"""

import os
import django


def asegurar_django():
    """Inicializa Django si no se encuentra configurado en el entorno actual."""
    if not os.environ.get("DJANGO_SETTINGS_MODULE"):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reservas_upb.settings")
    try:
        django.setup()
    except RuntimeError:
        # Django ya está configurado
        pass
