"""
reservas/apps.py
================
Configuración de la aplicación reservas y adaptaciones para MongoDB.
Incluye monkey-patching preventivo para permisos con django-mongodb-backend.
"""

import django.contrib.auth.apps as auth_apps_module
from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig
from django.contrib.auth.apps import AuthConfig
from django.contrib.contenttypes.apps import ContentTypesConfig


class ReservasConfig(AppConfig):
    """Configuración principal de la app de reservas."""
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
    name = "reservas"
    verbose_name = "Sistema de Reservas UPB"


class MongoAdminConfig(AdminConfig):
    """Configuración del Admin adaptada para MongoDB."""
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoAuthConfig(AuthConfig):
    """Configuración de Autenticación adaptada para MongoDB."""
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"

    def ready(self):
        # django-mongodb-backend tiene una incompatibilidad conocida con la creación
        # automática de permisos en post_migrate. Reemplazamos por una función no-op
        # antes de que Django conecte la señal post_migrate.
        def _no_crear_permisos(**kwargs):
            pass

        auth_apps_module.create_permissions = _no_crear_permisos
        super().ready()


class MongoContentTypesConfig(ContentTypesConfig):
    """Configuración de ContentTypes adaptada para MongoDB."""
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"