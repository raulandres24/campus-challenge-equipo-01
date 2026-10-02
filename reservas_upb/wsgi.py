"""
reservas_upb/wsgi.py
====================
Configuración WSGI para el proyecto de reservas UPB.
Expone la variable llamable de nivel de módulo `application` para servidores WSGI.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reservas_upb.settings')

application = get_wsgi_application()

