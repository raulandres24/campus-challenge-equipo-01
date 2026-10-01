import django.contrib.auth.apps as auth_apps_module
from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig
from django.contrib.auth.apps import AuthConfig
from django.contrib.contenttypes.apps import ContentTypesConfig


class ReservasConfig(AppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
    name = "reservas"


class MongoAdminConfig(AdminConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoAuthConfig(AuthConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"

    def ready(self):
        # django-mongodb-backend tiene un bug conocido con la creación
        # automática de permisos. La reemplazamos por una función vacía
        # ANTES de que Django la conecte a la señal post_migrate.
        def _no_crear_permisos(**kwargs):
            pass

        auth_apps_module.create_permissions = _no_crear_permisos
        super().ready()


class MongoContentTypesConfig(ContentTypesConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"