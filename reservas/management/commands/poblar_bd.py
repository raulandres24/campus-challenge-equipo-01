"""
management/commands/poblar_bd.py
=================================
Populate la base de datos con datos de prueba realistas para el sistema
de reservas de salas UPB.

Uso:
    python manage.py poblar_bd            # Crea datos (seguro: no duplica)
    python manage.py poblar_bd --limpiar  # Borra todo y re-crea desde cero
"""

import datetime
import random

from django.core.management.base import BaseCommand
from django.utils import timezone

from reservas.models import Estudiante, Reserva, Sala
from reservas.services import ReservaRechazada, reservar_si_esta_disponible

# ---------------------------------------------------------------------------
# Datos semilla
# ---------------------------------------------------------------------------

SALAS_MOCK = [
    {"nombre": "Sala Alfa",  "en_mantenimiento": False},
    {"nombre": "Sala Beta",  "en_mantenimiento": False},
    {"nombre": "Sala Gamma", "en_mantenimiento": True},   # Fuera de servicio
    {"nombre": "Sala Delta", "en_mantenimiento": False},
    {"nombre": "Sala Omega", "en_mantenimiento": False},
]

ESTUDIANTES_MOCK = [
    {"codigo": "U-92001", "nombres": "Hugo",      "apellidos": "Zúñiga",    "activo": True,  "matricula": True},
    {"codigo": "U-92002", "nombres": "Raúl",      "apellidos": "Vaca",      "activo": True,  "matricula": True},
    {"codigo": "U-92003", "nombres": "Alejandro", "apellidos": "Párraga",   "activo": True,  "matricula": True},
    {"codigo": "U-92004", "nombres": "Lucía",     "apellidos": "Méndez",    "activo": True,  "matricula": True},
    {"codigo": "U-92005", "nombres": "Carlos",    "apellidos": "Torrico",   "activo": True,  "matricula": False},  # Sin matrícula
    {"codigo": "U-92006", "nombres": "Valeria",   "apellidos": "Flores",    "activo": True,  "matricula": True},
    {"codigo": "U-92007", "nombres": "Sebastián", "apellidos": "Gutiérrez", "activo": False, "matricula": True},  # Inactivo
    {"codigo": "U-92008", "nombres": "Daniela",   "apellidos": "Castro",    "activo": True,  "matricula": True},
    {"codigo": "U-92009", "nombres": "Andrés",    "apellidos": "Romero",    "activo": True,  "matricula": True},
    {"codigo": "U-92010", "nombres": "Fernanda",  "apellidos": "Salinas",   "activo": True,  "matricula": True},
]

# Bloques horarios predefinidos (hora_inicio, hora_fin)
BLOQUES_HORARIOS = [
    (datetime.time(7, 0),  datetime.time(9, 0)),
    (datetime.time(9, 30), datetime.time(11, 30)),
    (datetime.time(12, 0), datetime.time(14, 0)),
    (datetime.time(14, 30), datetime.time(16, 30)),
    (datetime.time(17, 0), datetime.time(19, 0)),
]


# ---------------------------------------------------------------------------
# Helpers privados del comando
# ---------------------------------------------------------------------------

def _crear_salas(stdout) -> list[Sala]:
    salas = []
    for datos in SALAS_MOCK:
        sala, creada = Sala.objects.get_or_create(
            nombre=datos["nombre"],
            defaults={"en_mantenimiento": datos["en_mantenimiento"]},
        )
        estado = "[OK] creada" if creada else "[skip] ya existía"
        stdout.write(f"  Sala '{sala.nombre}' — {estado}")
        salas.append(sala)
    return salas


def _crear_estudiantes(stdout) -> list[Estudiante]:
    estudiantes = []
    for d in ESTUDIANTES_MOCK:
        est, creado = Estudiante.objects.get_or_create(
            codigo_estudiante=d["codigo"],
            defaults={
                "nombres": d["nombres"],
                "apellidos": d["apellidos"],
                "esta_activo": d["activo"],
                "matricula_pagada": d["matricula"],
            },
        )
        estado = "[OK] creado" if creado else "[skip] ya existía"
        stdout.write(f"  Estudiante '{est}' — {estado}")
        estudiantes.append(est)
    return estudiantes


def _generar_reservas(salas: list[Sala], estudiantes: list[Estudiante], stdout) -> None:
    """Genera reservas aleatorias para los próximos 14 días.

    Usa services.reservar_si_esta_disponible para respetar todas las
    reglas de negocio (buffer, matrícula, mantenimiento, etc.).
    """
    hoy = timezone.localdate()
    salas_disponibles = [s for s in salas if not s.en_mantenimiento]
    estudiantes_habilitados = [e for e in estudiantes if e.puede_reservar]

    creadas = 0
    rechazadas = 0

    # Intentamos ~30 reservas distribuidas en los próximos 14 días
    intentos = [
        (
            hoy + datetime.timedelta(days=random.randint(0, 13)),
            random.choice(salas_disponibles),
            random.choice(estudiantes_habilitados),
            random.choice(BLOQUES_HORARIOS),
        )
        for _ in range(30)
    ]

    for fecha, sala, estudiante, (inicio, fin) in intentos:
        try:
            reservar_si_esta_disponible(
                estudiante=estudiante,
                sala=sala,
                fecha=fecha,
                hora_inicio=inicio,
                hora_fin=fin,
            )
            stdout.write(
                f"  [OK] Reserva: {estudiante.nombres} en {sala.nombre} "
                f"el {fecha} {inicio:%H:%M}-{fin:%H:%M}"
            )
            creadas += 1
        except ReservaRechazada as e:
            stdout.write(f"  [skip] Rechazada ({e})")
            rechazadas += 1

    stdout.write(f"\n  Total: {creadas} reservas creadas, {rechazadas} rechazadas por reglas de negocio.")


# ---------------------------------------------------------------------------
# Comando Django
# ---------------------------------------------------------------------------

class Command(BaseCommand):
    help = (
        "Puebla la base de datos con datos de prueba (Estudiantes, Salas y Reservas). "
        "Usa --limpiar para borrar todo antes de crear."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--limpiar",
            action="store_true",
            help="Elimina todos los datos existentes antes de crear los nuevos.",
        )

    def handle(self, *args, **options):
        if options["limpiar"]:
            self.stdout.write(self.style.WARNING("[WARN] Limpiando base de datos..."))
            Reserva.objects.all().delete()
            Estudiante.objects.all().delete()
            Sala.objects.all().delete()
            self.stdout.write("  Datos eliminados.\n")

        self.stdout.write(self.style.HTTP_INFO("-> Creando salas..."))
        salas = _crear_salas(self.stdout)

        self.stdout.write(self.style.HTTP_INFO("\n-> Creando estudiantes..."))
        estudiantes = _crear_estudiantes(self.stdout)

        self.stdout.write(self.style.HTTP_INFO("\n-> Generando reservas..."))
        _generar_reservas(salas, estudiantes, self.stdout)

        self.stdout.write(self.style.SUCCESS("\n[DONE] Base de datos poblada correctamente."))
