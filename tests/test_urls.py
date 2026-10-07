"""
tests/test_urls.py
==================
Pruebas del enrutamiento de sesión (botón "Salir").

No necesitan MongoDB: solo resuelven URLs y llaman a la vista de logout
con un usuario anónimo (no se guarda ninguna sesión).
"""

from django.test import Client
from django.urls import resolve, reverse

from reservas import views


def test_url_logout_apunta_a_la_vista_propia():
    assert reverse("logout") == "/logout/"
    assert resolve("/logout/").func is views.logout_view


def test_url_login_apunta_a_la_vista_propia():
    assert reverse("login") == "/login/"
    assert resolve("/login/").func is views.login_view


def test_boton_salir_con_get_redirige_al_login():
    respuesta = Client().get(reverse("logout"))
    assert respuesta.status_code == 302
    assert respuesta["Location"] == reverse("login")
