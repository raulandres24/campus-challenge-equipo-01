"""
management/commands/poblar_bd.py
=================================
Puebla la base de datos con datos de prueba realistas para el sistema
de reservas de salas UPB, incluyendo usuarios con poderes especiales y estudiantes.

Uso:
    python manage.py poblar_bd            # Crea datos (seguro: no duplica)
    python manage.py poblar_bd --limpiar  # Borra todo y re-crea desde cero
"""

import datetime
import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from reservas.models import Estudiante, Reserva, Sala
from reservas.services import ReservaRechazada, reservar_si_esta_disponible

# ---------------------------------------------------------------------------
# Datos semilla
# ---------------------------------------------------------------------------

USUARIOS_ESPECIALES = [
    {
        "username": "sbarrientos",
        "first_name": "Sergio",
        "last_name": "Barrientos",
        "email": "sbarrientos@upb.edu",
        "is_staff": True,
        "is_superuser": True,
        "password": "password",
    },
    {
        "username": "hugozuniga770",
        "first_name": "Hugo",
        "last_name": "Zúñiga",
        "email": "hzuniga@upb.edu",
        "is_staff": True,
        "is_superuser": True,
        "password": "password",
    },
    {
        "username": "rvaca",
        "first_name": "Raúl",
        "last_name": "Vaca",
        "email": "rvaca@upb.edu",
        "is_staff": True,
        "is_superuser": True,
        "password": "password",
    },
    {
        "username": "aparraga",
        "first_name": "Alejandro",
        "last_name": "Párraga",
        "email": "aparraga@upb.edu",
        "is_staff": True,
        "is_superuser": True,
        "password": "password",
    },
    {
        "username": "admin",
        "first_name": "Administrador",
        "last_name": "UPB",
        "email": "admin@upb.edu",
        "is_staff": True,
        "is_superuser": True,
        "password": "password",
    },
]

USUARIOS_ESTUDIANTES = [
    {"username": "lucia.mendez", "first_name": "Lucía", "last_name": "Méndez", "password": "password"},
    {"username": "carlos.torrico", "first_name": "Carlos", "last_name": "Torrico", "password": "password"},
    {"username": "valeria.flores", "first_name": "Valeria", "last_name": "Flores", "password": "password"},
    {"username": "daniela.castro", "first_name": "Daniela", "last_name": "Castro", "password": "password"},
    {"username": "andres.romero", "first_name": "Andrés", "last_name": "Romero", "password": "password"},
    {"username": "fernanda.salinas", "first_name": "Fernanda", "last_name": "Salinas", "password": "password"},
]

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

# Bloques horarios predefinidos con intervalos de desalojo (15 min)
BLOQUES_HORARIOS = [
    (datetime.time(7, 45),  datetime.time(9, 45)),
    (datetime.time(10, 0),  datetime.time(12, 0)),
    (datetime.time(12, 15), datetime.time(14, 15)),
    (datetime.time(14, 30), datetime.time(16, 30)),
    (datetime.time(16, 45), datetime.time(18, 45)),
    (datetime.time(19, 0),  datetime.time(21, 0)),
]


def _crear_usuarios(stdout) -> None:
    # 1. Crear usuarios con poderes especiales
    for u in USUARIOS_ESPECIALES:
        user = User.objects.filter(username=u["username"]).first()
        if not user:
            user = User.objects.create_user(
                username=u["username"],
                email=u.get("email", ""),
                first_name=u["first_name"],
                last_name=u["last_name"],
                is_staff=u["is_staff"],
                is_superuser=u["is_superuser"],
            )
            user.set_password(u["password"])
            user.save()
            stdout.write(f"  [OK] Usuario con Poderes '{user.username}' ({u['first_name']} {u['last_name']})")
        else:
            user.first_name = u["first_name"]
            user.last_name = u["last_name"]
            user.is_staff = u["is_staff"]
            user.is_superuser = u["is_superuser"]
            user.set_password(u["password"])
            user.save()
            stdout.write(f"  [skip] Usuario '{user.username}' actualizado con poderes")

    # 2. Crear usuarios estudiantes
    for u in USUARIOS_ESTUDIANTES:
        user = User.objects.filter(username=u["username"]).first()
        if not user:
            user = User.objects.create_user(
                username=u["username"],
                first_name=u["first_name"],
                last_name=u["last_name"],
                is_staff=False,
                is_superuser=False,
            )
            user.set_password(u["password"])
            user.save()
            stdout.write(f"  [OK] Estudiante usuario '{user.username}'")


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
    hoy = timezone.localdate()
    salas_disponibles = [s for s in salas if not s.en_mantenimiento]
    estudiantes_habilitados = [e for e in estudiantes if e.puede_reservar]

    creadas = 0
    rechazadas = 0

    # Reservas para hoy (para que el calendario se vea lleno y hermoso de inmediato)
    for sala in salas_disponibles:
        # Asignar 2 o 3 bloques para hoy en cada sala
        bloques_hoy = random.sample(BLOQUES_HORARIOS, 3)
        for inicio, fin in bloques_hoy:
            estudiante = random.choice(estudiantes_habilitados)
            try:
                reservar_si_esta_disponible(
                    estudiante=estudiante,
                    sala=sala,
                    fecha=hoy,
                    hora_inicio=inicio,
                    hora_fin=fin,
                )
                creadas += 1
            except ReservaRechazada:
                rechazadas += 1

    # Intentamos más reservas para los próximos 7 días
    for _ in range(25):
        fecha = hoy + datetime.timedelta(days=random.randint(1, 7))
        sala = random.choice(salas_disponibles)
        estudiante = random.choice(estudiantes_habilitados)
        inicio, fin = random.choice(BLOQUES_HORARIOS)
        try:
            reservar_si_esta_disponible(
                estudiante=estudiante,
                sala=sala,
                fecha=fecha,
                hora_inicio=inicio,
                hora_fin=fin,
            )
            creadas += 1
        except ReservaRechazada:
            rechazadas += 1

    stdout.write(f"\n  Total: {creadas} reservas activas creadas en MongoDB.")


class Command(BaseCommand):
    help = (
        "Puebla la base de datos con usuarios de login (incluyendo poderes especiales), "
        "estudiantes, salas y reservas de prueba. Usa --limpiar para reiniciar desde cero."
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
            self.stdout.write("  Datos de negocio eliminados.\n")

        self.stdout.write(self.style.HTTP_INFO("-> Configurando usuarios del sistema (Poderes Especiales y Estudiantes)..."))
        _crear_usuarios(self.stdout)

        self.stdout.write(self.style.HTTP_INFO("\n-> Creando salas..."))
        salas = _crear_salas(self.stdout)

        self.stdout.write(self.style.HTTP_INFO("\n-> Creando estudiantes..."))
        estudiantes = _crear_estudiantes(self.stdout)

        self.stdout.write(self.style.HTTP_INFO("\n-> Generando reservas para el calendario..."))
        _generar_reservas(salas, estudiantes, self.stdout)

        self.stdout.write(self.style.SUCCESS("\n[DONE] Base de datos poblada y usuarios con poderes listos para logueo."))
