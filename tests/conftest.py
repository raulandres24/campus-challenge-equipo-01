"""
tests/conftest.py
=================
Configuración global de pytest y fixtures para inicializar Django y MongoDB.

Base de datos de pruebas (exigencia del encargo: "probar sin modificar una
base de datos real"):

- Las pruebas que usan MongoDB piden el fixture ``bd_de_prueba``. Este crea
  una base aparte llamada ``test_<MONGO_DB_NAME>`` (por ejemplo
  ``test_reservas_upb``), le aplica las migraciones y la borra al terminar.
  La base real (``reservas_upb``) no se lee ni se modifica.
- Las pruebas puras (horarios, URLs, reglas sin base de datos) no piden ese
  fixture y corren aunque MongoDB esté apagado.
"""

import os
import django
import pytest

# Inicializar Django antes de cualquier test
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reservas_upb.settings")
django.setup()

from django.db import connection

from reservas.models import Estudiante, Reserva, Sala


@pytest.fixture(scope="session")
def bd_de_prueba():
    """Crea la base ``test_...`` una vez por corrida y la elimina al final."""
    nombre_real = connection.settings_dict["NAME"]
    connection.creation.create_test_db(verbosity=0, autoclobber=True, keepdb=False)
    nombre_prueba = connection.settings_dict["NAME"]
    # Freno de seguridad: nunca correr pruebas contra la base real.
    assert nombre_prueba != nombre_real and nombre_prueba.startswith("test_"), (
        f"Las pruebas iban a usar la base '{nombre_prueba}'. Se detienen por seguridad."
    )
    yield nombre_prueba
    connection.creation.destroy_test_db(nombre_real, verbosity=0)


def _limpiar_datos_test():
    """Limpia registros de prueba en MongoDB sin usar queries JOIN que no soporta Mongo."""
    # 1. Obtener IDs de estudiantes de test
    test_estudiantes = list(Estudiante.objects.filter(codigo_estudiante__startswith="TEST-"))
    test_est_ids = [e.id for e in test_estudiantes]

    # 2. Obtener IDs de salas de test
    test_salas = list(Sala.objects.filter(nombre__startswith="Test Sala"))
    test_sala_ids = [s.id for s in test_salas]

    # 3. Borrar reservas asociadas a los IDs
    if test_est_ids:
        Reserva.objects.filter(estudiante_id__in=test_est_ids).delete()
    if test_sala_ids:
        Reserva.objects.filter(sala_id__in=test_sala_ids).delete()

    # 4. Borrar entidades principales por ID
    if test_est_ids:
        Estudiante.objects.filter(id__in=test_est_ids).delete()
    if test_sala_ids:
        Sala.objects.filter(id__in=test_sala_ids).delete()


@pytest.fixture
def limpiar_reservas_test(bd_de_prueba):
    """Limpia los registros de prueba antes y después de cada prueba que usa MongoDB.

    Ya no es automática para todas las pruebas: la piden los módulos que usan
    la base (con ``pytestmark``) para que las pruebas puras no necesiten MongoDB.
    """
    _limpiar_datos_test()
    yield
    _limpiar_datos_test()


@pytest.fixture
def estudiante_habilitado_db(limpiar_reservas_test):
    """Estudiante activo y con matrícula pagada en MongoDB."""
    estudiante, _ = Estudiante.objects.get_or_create(
        codigo_estudiante="TEST-E01",
        defaults={
            "nombres": "Estudiante",
            "apellidos": "Habilitado",
            "esta_activo": True,
            "matricula_pagada": True,
        },
    )
    estudiante.esta_activo = True
    estudiante.matricula_pagada = True
    estudiante.save()
    return estudiante


@pytest.fixture
def estudiante_inactivo_db(limpiar_reservas_test):
    """Estudiante inactivo en MongoDB."""
    estudiante, _ = Estudiante.objects.get_or_create(
        codigo_estudiante="TEST-E02",
        defaults={
            "nombres": "Estudiante",
            "apellidos": "Inactivo",
            "esta_activo": False,
            "matricula_pagada": True,
        },
    )
    estudiante.esta_activo = False
    estudiante.matricula_pagada = True
    estudiante.save()
    return estudiante


@pytest.fixture
def estudiante_sin_matricula_db(limpiar_reservas_test):
    """Estudiante sin matrícula pagada en MongoDB."""
    estudiante, _ = Estudiante.objects.get_or_create(
        codigo_estudiante="TEST-E03",
        defaults={
            "nombres": "Estudiante",
            "apellidos": "Deudor",
            "esta_activo": True,
            "matricula_pagada": False,
        },
    )
    estudiante.esta_activo = True
    estudiante.matricula_pagada = False
    estudiante.save()
    return estudiante


@pytest.fixture
def sala_disponible_db(limpiar_reservas_test):
    """Sala habilitada y sin mantenimiento en MongoDB."""
    sala, _ = Sala.objects.get_or_create(
        nombre="Test Sala Alfa",
        defaults={"en_mantenimiento": False},
    )
    sala.en_mantenimiento = False
    sala.save()
    return sala


@pytest.fixture
def sala_mantenimiento_db(limpiar_reservas_test):
    """Sala en mantenimiento en MongoDB."""
    sala, _ = Sala.objects.get_or_create(
        nombre="Test Sala Mantenimiento",
        defaults={"en_mantenimiento": True},
    )
    sala.en_mantenimiento = True
    sala.save()
    return sala
