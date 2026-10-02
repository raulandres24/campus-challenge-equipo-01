"""
tests/conftest.py
=================
Configuración global de pytest y fixtures para inicializar Django y MongoDB.
"""

import os
import django
import pytest

# Inicializar Django antes de cualquier test
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reservas_upb.settings")
django.setup()

from reservas.models import Estudiante, Reserva, Sala


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


@pytest.fixture(autouse=True)
def limpiar_reservas_test():
    """Fixture automática que limpia las reservas de test antes y después de cada prueba."""
    _limpiar_datos_test()
    yield
    _limpiar_datos_test()


@pytest.fixture
def estudiante_habilitado_db():
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
def estudiante_inactivo_db():
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
def estudiante_sin_matricula_db():
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
def sala_disponible_db():
    """Sala habilitada y sin mantenimiento en MongoDB."""
    sala, _ = Sala.objects.get_or_create(
        nombre="Test Sala Alfa",
        defaults={"en_mantenimiento": False},
    )
    sala.en_mantenimiento = False
    sala.save()
    return sala


@pytest.fixture
def sala_mantenimiento_db():
    """Sala en mantenimiento en MongoDB."""
    sala, _ = Sala.objects.get_or_create(
        nombre="Test Sala Mantenimiento",
        defaults={"en_mantenimiento": True},
    )
    sala.en_mantenimiento = True
    sala.save()
    return sala
