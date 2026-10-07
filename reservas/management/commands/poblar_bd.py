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
from reservas.niveles import nivel_puede_usar_sala
from reservas.padron import cargar_padron
from reservas.services import ReservaRechazada, reservar_si_esta_disponible

# ---------------------------------------------------------------------------
# Datos semilla
# ---------------------------------------------------------------------------

# Salas del campus. A y E son exclusivas de postgrado y doctorado; las demás, de pregrado.
# Sala H queda en mantenimiento para que se vea ese estado en la demostración.
SALAS_MOCK = [
    {"nombre": "Sala A", "en_mantenimiento": False, "exclusiva_posgrado": True},
    {"nombre": "Sala B", "en_mantenimiento": False, "exclusiva_posgrado": False},
    {"nombre": "Sala C", "en_mantenimiento": False, "exclusiva_posgrado": False},
    {"nombre": "Sala D", "en_mantenimiento": False, "exclusiva_posgrado": False},
    {"nombre": "Sala E", "en_mantenimiento": False, "exclusiva_posgrado": True},
    {"nombre": "Sala F", "en_mantenimiento": False, "exclusiva_posgrado": False},
    {"nombre": "Sala H", "en_mantenimiento": True,  "exclusiva_posgrado": False},  # Fuera de servicio
    {"nombre": "Sala J", "en_mantenimiento": False, "exclusiva_posgrado": False},
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


def _crear_superusuario(stdout) -> None:
    """Superusuario solo para el sitio /admin/ de Django. Las personas entran por el padrón."""
    user, creado = User.objects.get_or_create(
        username="admin",
        defaults={"first_name": "Administrador", "last_name": "UPB", "is_staff": True, "is_superuser": True},
    )
    if creado:
        user.set_password("password")
        user.save()
    stdout.write(f"  Superusuario 'admin' (solo /admin/) — {'[OK] creado' if creado else '[skip] ya existía'}")


def _crear_salas(stdout) -> list[Sala]:
    salas = []
    for datos in SALAS_MOCK:
        sala, creada = Sala.objects.get_or_create(
            nombre=datos["nombre"],
            defaults={
                "en_mantenimiento": datos["en_mantenimiento"],
                "exclusiva_posgrado": datos["exclusiva_posgrado"],
            },
        )
        estado = "[OK] creada" if creada else "[skip] ya existía"
        stdout.write(f"  Sala '{sala.nombre}' — {estado}")
        salas.append(sala)
    return salas


def _crear_estudiantes(stdout) -> list[Estudiante]:
    """Crea los estudiantes del padrón simulado (los docentes y administradores no reservan)."""
    estudiantes = []
    for persona in cargar_padron():
        if persona.get("rol") != "estudiante":
            continue
        est, creado = Estudiante.objects.get_or_create(
            codigo_estudiante=persona["codigo"],
            defaults={
                "nombres": persona["nombres"],
                "apellidos": persona["apellidos"],
                "esta_activo": persona["activo"],
                "matricula_pagada": persona["matricula_vigente"],
                "nivel": persona["nivel"],
            },
        )
        estado = "[OK] creado" if creado else "[skip] ya existía"
        stdout.write(f"  Estudiante '{est}' ({est.nivel}) — {estado}")
        estudiantes.append(est)
    return estudiantes


def _generar_reservas(salas: list[Sala], estudiantes: list[Estudiante], stdout) -> None:
    hoy = timezone.localdate()
    salas_disponibles = [s for s in salas if not s.en_mantenimiento]
    estudiantes_habilitados = [e for e in estudiantes if e.puede_reservar]

    def elegir_estudiante(sala):
        """Un estudiante habilitado cuyo nivel puede usar esa sala (A y E: postgrado y doctorado)."""
        candidatos = [e for e in estudiantes_habilitados if nivel_puede_usar_sala(e.nivel, sala.exclusiva_posgrado)]
        return random.choice(candidatos) if candidatos else None

    creadas = 0
    rechazadas = 0

    # Reservas para hoy (para que el calendario se vea lleno y hermoso de inmediato)
    for sala in salas_disponibles:
        # Asignar 2 o 3 bloques para hoy en cada sala
        bloques_hoy = random.sample(BLOQUES_HORARIOS, 3)
        for inicio, fin in bloques_hoy:
            estudiante = elegir_estudiante(sala)
            if estudiante is None:
                continue
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
        estudiante = elegir_estudiante(sala)
        if estudiante is None:
            continue
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
        "Puebla la base de datos con las salas, los estudiantes del padrón simulado y reservas "
        "de prueba. Las personas inician sesión con el padrón (datos/padron_upb.json). "
        "Usa --limpiar para reiniciar desde cero."
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

        self.stdout.write(self.style.HTTP_INFO("-> Superusuario del sitio /admin/..."))
        _crear_superusuario(self.stdout)

        self.stdout.write(self.style.HTTP_INFO("\n-> Creando salas..."))
        salas = _crear_salas(self.stdout)

        self.stdout.write(self.style.HTTP_INFO("\n-> Creando estudiantes..."))
        estudiantes = _crear_estudiantes(self.stdout)

        self.stdout.write(self.style.HTTP_INFO("\n-> Generando reservas para el calendario..."))
        _generar_reservas(salas, estudiantes, self.stdout)

        self.stdout.write(self.style.SUCCESS("\n[DONE] Base de datos poblada. Inicia sesión con una persona del padrón (ver README)."))
