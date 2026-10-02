"""
reservas/admin.py
=================
Configuración del panel de administración estándar de Django para los modelos
de Estudiante, Sala y Reserva en MongoDB.
"""

from django.contrib import admin

from .models import Estudiante, Reserva, Sala


@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    """Panel de administración para Estudiantes."""
    list_display = ("codigo_estudiante", "apellidos", "nombres", "esta_activo", "matricula_pagada")
    list_filter = ("esta_activo", "matricula_pagada")
    search_fields = ("codigo_estudiante", "nombres", "apellidos")


@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    """Panel de administración para Salas."""
    list_display = ("nombre", "en_mantenimiento")
    list_filter = ("en_mantenimiento",)


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    """Panel de administración para Reservas."""
    list_display = ("sala", "estudiante", "fecha", "hora_inicio", "hora_fin", "estado")
    list_filter = ("estado", "sala", "fecha")
    search_fields = ("estudiante__nombres", "estudiante__apellidos", "estudiante__codigo_estudiante")
    date_hierarchy = "fecha"
