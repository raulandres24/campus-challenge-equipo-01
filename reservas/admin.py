from django.contrib import admin

from .models import Estudiante, Reserva, Sala


@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ("codigo_estudiante", "apellidos", "nombres", "esta_activo", "matricula_pagada")
    list_filter = ("esta_activo", "matricula_pagada")
    search_fields = ("codigo_estudiante", "nombres", "apellidos")


@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "en_mantenimiento")
    list_filter = ("en_mantenimiento",)


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ("sala", "estudiante", "fecha", "hora_inicio", "hora_fin", "estado")
    list_filter = ("estado", "sala", "fecha")
    search_fields = ("estudiante__nombres", "estudiante__apellidos", "estudiante__codigo_estudiante")
    date_hierarchy = "fecha"