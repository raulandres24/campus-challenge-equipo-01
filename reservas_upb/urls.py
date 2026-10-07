"""
reservas_upb/urls.py
====================
Enrutador raíz del proyecto Django.

Nota: no se incluye "django.contrib.auth.urls". Sus nombres de URL
("login", "logout") chocaban con los de reservas/urls.py y hacían que
{% url 'logout' %} apuntara a la vista de Django (/accounts/logout/),
que en Django 5 solo acepta POST. Por eso el botón "Salir" daba 405.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("reservas.urls")),
]
