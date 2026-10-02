"""
reservas_upb/urls.py
====================
Enrutador raíz del proyecto Django.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("reservas.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
]