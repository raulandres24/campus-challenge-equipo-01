"""
reservas_upb/asgi.py
====================
Configuración ASGI para el proyecto de reservas UPB.
Expone la variable llamable de nivel de módulo `application` para servidores ASGI.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reservas_upb.settings')

application = get_asgi_application()

