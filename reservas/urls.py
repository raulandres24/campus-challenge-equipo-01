"""
reservas/urls.py
================
Enrutamiento de la aplicación de reservas UPB.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Vistas Web Principales
    path("", views.inicio_view, name="inicio"),
    path("panel/", views.admin_dashboard_view, name="admin_dashboard"),
    path("admin-dashboard/", views.admin_dashboard_view, name="admin_dashboard_alias"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # APIs Públicas y de Reserva
    path("api/reservar/", views.api_reservar, name="api_reservar"),
    path("api/cancelar/", views.api_cancelar_reserva, name="api_cancelar"),
    path("api/modificar-reserva/", views.api_modificar_reserva, name="api_modificar_reserva"),

    # APIs Exclusivas de Administradores con Poderes Especiales
    path("api/editar-reserva/", views.api_editar_reserva, name="api_editar_reserva"),
    path("api/eliminar-reserva/", views.api_eliminar_reserva_definitiva, name="api_eliminar_reserva"),
    path("api/toggle-mantenimiento/", views.api_toggle_mantenimiento, name="api_toggle_mantenimiento"),
    path("api/crear-sala/", views.api_crear_sala, name="api_crear_sala"),
]
