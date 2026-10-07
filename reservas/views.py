"""
reservas/views.py
=================
Controladores de vistas para la interfaz web del sistema de reservas UPB.
Incluye autenticación, vista de estudiante, panel de administración con poderes especiales,
calendario visual, edición y gestión completa de reservas y salas.
"""

from __future__ import annotations

import datetime
import json
import re

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from proyecto.clases.horarios import minutos_a_time, parsear_horas, validar_rango_horario
from proyecto.clases.sistema_reservas import reservar_si_es_posible
from .models import Estudiante, Reserva, Sala
from .niveles import nivel_puede_usar_sala
from .padron import verificar_credenciales
from .permisos import es_duenio_de_reserva, estudiante_del_usuario, obtener_info_usuario, tiene_poderes_especiales
from .agenda import armar_agenda
from .services import ReservaRechazada, ReservaYaComenzo, inicio_de_reserva, modificar_reserva_si_esta_disponible

# Horarios estándar universitarios UPB
BLOQUES_PREDEFINIDOS = [
    {"label": "07:45 - 09:45", "inicio": "07:45", "fin": "09:45"},
    {"label": "10:00 - 12:00", "inicio": "10:00", "fin": "12:00"},
    {"label": "12:15 - 14:15", "inicio": "12:15", "fin": "14:15"},
    {"label": "14:30 - 16:30", "inicio": "14:30", "fin": "16:30"},
    {"label": "16:45 - 18:45", "inicio": "16:45", "fin": "18:45"},
    {"label": "19:00 - 21:00", "inicio": "19:00", "fin": "21:00"},
]

COLORES_SALAS = {
    "Sala A": {"bg": "rgba(16, 185, 129, 0.15)", "border": "#10b981", "text": "#065f46"},
    "Sala B": {"bg": "rgba(59, 130, 246, 0.15)", "border": "#3b82f6", "text": "#1e40af"},
    "Sala C": {"bg": "rgba(168, 85, 247, 0.15)", "border": "#a855f7", "text": "#6b21a8"},
    "Sala D": {"bg": "rgba(245, 158, 11, 0.15)", "border": "#f59e0b", "text": "#92400e"},
    "Sala E": {"bg": "rgba(20, 184, 166, 0.15)", "border": "#14b8a6", "text": "#115e59"},
    "Sala F": {"bg": "rgba(236, 72, 153, 0.15)", "border": "#ec4899", "text": "#9d174d"},
    "Sala H": {"bg": "rgba(239, 68, 68, 0.15)", "border": "#ef4444", "text": "#991b1b"},
    "Sala J": {"bg": "rgba(99, 102, 241, 0.15)", "border": "#6366f1", "text": "#3730a3"},
}

CODIGO_VALIDO = re.compile(r"\d{5}")  # los códigos de la UPB (estudiantes y personal) tienen 5 dígitos


def _destino_tras_login(request: HttpRequest, user) -> str:
    """A dónde ir después de iniciar sesión (``next`` solo si es de este mismo sitio)."""
    siguiente = request.GET.get("next", "")
    if siguiente and url_has_allowed_host_and_scheme(siguiente, allowed_hosts={request.get_host()}):
        return siguiente
    return "admin_dashboard" if tiene_poderes_especiales(user) else "inicio"


def login_view(request: HttpRequest) -> HttpResponse:
    """Inicio de sesión único para estudiantes, docentes y administradores.

    Se piden código (5 dígitos), correo institucional y contraseña, y se verifican contra
    el padrón simulado (``reservas/padron.py``). El rol sale del padrón, no de la pantalla.
    Si algún dato falla se muestra un mensaje genérico, para no revelar qué códigos existen.
    """
    if request.user.is_authenticated:
        return redirect(_destino_tras_login(request, request.user))

    error_mensaje = None
    if request.method == "POST":
        codigo = request.POST.get("codigo", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        if not CODIGO_VALIDO.fullmatch(codigo):
            error_mensaje = "El código tiene 5 dígitos, por ejemplo 94210."
        else:
            persona = verificar_credenciales(codigo, email, password)
            if persona is None:
                error_mensaje = "Código, correo o contraseña incorrectos."
            elif not persona["activo"]:
                error_mensaje = "Tu registro en el padrón no está activo. Consulta en Registros de la UPB."
            else:
                user = authenticate(request, codigo=codigo, email=email, password=password)
                login(request, user, backend="reservas.padron.PadronBackend")
                return redirect(_destino_tras_login(request, user))

    return render(request, "web/login.html", {
        "error_mensaje": error_mensaje,
        # Los accesos de demostración (con la contraseña a la vista) solo existen en desarrollo.
        "mostrar_demo": settings.DEBUG,
    })


def logout_view(request: HttpRequest) -> HttpResponse:
    """Cierra la sesión y redirige al login."""
    logout(request)
    return redirect("login")


@login_required(login_url="/login/")
def inicio_view(request: HttpRequest) -> HttpResponse:
    """Vista pública de reservas para estudiantes con el calendario de disponibilidad."""
    hoy = timezone.localdate()
    fecha_param = request.GET.get("fecha")

    if fecha_param:
        try:
            fecha_seleccionada = datetime.datetime.strptime(fecha_param, "%Y-%m-%d").date()
        except ValueError:
            fecha_seleccionada = hoy
    else:
        fecha_seleccionada = hoy

    sala_filtro = request.GET.get("sala", "todas")
    salas = list(Sala.objects.all().order_by("nombre"))
    user_info = obtener_info_usuario(request.user)
    estudiante_asociado = estudiante_del_usuario(request.user)
    if not user_info["tiene_poderes"] and estudiante_asociado is not None:
        # Un estudiante solo ve las salas de su nivel (A y E: postgrado y doctorado).
        salas = [s for s in salas if nivel_puede_usar_sala(estudiante_asociado.nivel, s.exclusiva_posgrado)]

    query_reservas = {"fecha": fecha_seleccionada, "estado": Reserva.ESTADO_CONFIRMADA}
    if sala_filtro != "todas":
        query_reservas["sala__nombre"] = sala_filtro

    reservas = list(
        Reserva.objects.filter(**query_reservas)
        .select_related("estudiante", "sala")
        .order_by("hora_inicio")
    )

    ahora = timezone.now()
    reservas_calendario = []
    for r in reservas:
        color = COLORES_SALAS.get(
            r.sala.nombre,
            {"bg": "rgba(99, 102, 241, 0.15)", "border": "#6366f1", "text": "#3730a3"},
        )
        reservas_calendario.append({
            "id": str(r.id),
            "sala_nombre": r.sala.nombre,
            "estudiante_nombre": f"{r.estudiante.nombres} {r.estudiante.apellidos}",
            "estudiante_codigo": r.estudiante.codigo_estudiante,
            "hora_inicio": r.hora_inicio.strftime("%H:%M"),
            "hora_fin": r.hora_fin.strftime("%H:%M"),
            "color_bg": color["bg"],
            "color_border": color["border"],
            "color_text": color["text"],
            "es_propia": es_duenio_de_reserva(request.user, r),
            "puede_gestionar": user_info["tiene_poderes"] or es_duenio_de_reserva(request.user, r),
            "ya_comenzo": inicio_de_reserva(r) <= ahora,
            "fecha": r.fecha.strftime("%Y-%m-%d"),
        })

    filas_agenda, agenda_por_sala = armar_agenda(salas, reservas_calendario, BLOQUES_PREDEFINIDOS)

    estudiantes_habilitados = list(
        Estudiante.objects.filter(esta_activo=True, matricula_pagada=True).order_by("apellidos")
    )

    dias_semana_es = {0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"}
    meses_es = {1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio", 7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"}

    fecha_formateada = f"{fecha_seleccionada.day} de {meses_es[fecha_seleccionada.month]} de {fecha_seleccionada.year}"
    dia_nombre = dias_semana_es[fecha_seleccionada.weekday()]

    context = {
        "user_info": user_info,
        "hoy": hoy,
        "fecha_seleccionada": fecha_seleccionada,
        "fecha_iso": fecha_seleccionada.strftime("%Y-%m-%d"),
        "fecha_formateada": fecha_formateada,
        "dia_nombre": dia_nombre,
        "salas": salas,
        "sala_filtro": sala_filtro,
        "reservas": reservas,
        "reservas_calendario": reservas_calendario,
        "filas_agenda": filas_agenda,
        "agenda_por_sala": agenda_por_sala,
        "bloques_predefinidos": BLOQUES_PREDEFINIDOS,
        "estudiante_asociado": estudiante_asociado,
        "estudiantes_habilitados": estudiantes_habilitados,
        "tiene_poderes": user_info["tiene_poderes"],
    }

    return render(request, "web/inicio.html", context)


@login_required(login_url="/login/")
def admin_dashboard_view(request: HttpRequest) -> HttpResponse:
    """Panel de Control de Administrador exclusivo para Sergio Barrientos, Hugo Zúñiga,

    Raúl Vaca, Alejandro Párraga y Administradores del sistema con Poderes Especiales.
    Permite:
        - Ver el calendario visual con todas las salas.
        - Ver y buscar en el registro completo de todas las reservas de la base de datos de MongoDB.
        - Editar y mover fechas / horarios / salas de cualquier reserva.
        - Eliminar o cancelar reservas.
        - Activar o desactivar (mantenimiento) salas en vivo.
        - Crear nuevas salas de estudio.
    """
    if not tiene_poderes_especiales(request.user):
        return redirect("inicio")

    hoy = timezone.localdate()
    fecha_param = request.GET.get("fecha")

    if fecha_param:
        try:
            fecha_seleccionada = datetime.datetime.strptime(fecha_param, "%Y-%m-%d").date()
        except ValueError:
            fecha_seleccionada = hoy
    else:
        fecha_seleccionada = hoy

    salas = list(Sala.objects.all().order_by("nombre"))
    estudiantes = list(Estudiante.objects.all().order_by("apellidos", "nombres"))

    # Reservas para el calendario de la fecha
    reservas_fecha = list(
        Reserva.objects.filter(fecha=fecha_seleccionada, estado=Reserva.ESTADO_CONFIRMADA)
        .select_related("estudiante", "sala")
        .order_by("hora_inicio")
    )

    reservas_calendario = []
    for r in reservas_fecha:
        color = COLORES_SALAS.get(
            r.sala.nombre,
            {"bg": "rgba(99, 102, 241, 0.15)", "border": "#6366f1", "text": "#3730a3"},
        )
        reservas_calendario.append({
            "id": str(r.id),
            "sala_nombre": r.sala.nombre,
            "estudiante_nombre": f"{r.estudiante.nombres} {r.estudiante.apellidos}",
            "estudiante_codigo": r.estudiante.codigo_estudiante,
            "hora_inicio": r.hora_inicio.strftime("%H:%M"),
            "hora_fin": r.hora_fin.strftime("%H:%M"),
            "color_bg": color["bg"],
            "color_border": color["border"],
            "color_text": color["text"],
            "es_propia": True,
        })

    # Todas las reservas de MongoDB (Registro completo para el administrador)
    q_busqueda = request.GET.get("q", "").strip()
    query_todas = {}
    if request.GET.get("filtro_estado"):
        query_todas["estado"] = request.GET.get("filtro_estado")

    todas_las_reservas_qs = Reserva.objects.filter(**query_todas).select_related("estudiante", "sala").order_by("-fecha", "-hora_inicio")
    
    if q_busqueda:
        todas_las_reservas = [
            r for r in todas_las_reservas_qs
            if q_busqueda.lower() in r.estudiante.nombres.lower()
            or q_busqueda.lower() in r.estudiante.apellidos.lower()
            or q_busqueda.lower() in r.estudiante.codigo_estudiante.lower()
            or q_busqueda.lower() in r.sala.nombre.lower()
        ]
    else:
        todas_las_reservas = list(todas_las_reservas_qs[:100])

    # Métricas del Dashboard
    metricas = {
        "reservas_hoy": Reserva.objects.filter(fecha=hoy, estado=Reserva.ESTADO_CONFIRMADA).count(),
        "total_historico": Reserva.objects.count(),
        "salas_habilitadas": Sala.objects.filter(en_mantenimiento=False).count(),
        "salas_mantenimiento": Sala.objects.filter(en_mantenimiento=True).count(),
        "estudiantes_activos": Estudiante.objects.filter(esta_activo=True, matricula_pagada=True).count(),
    }

    user_info = obtener_info_usuario(request.user)

    dias_semana_es = {0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"}
    meses_es = {1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio", 7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"}

    fecha_formateada = f"{fecha_seleccionada.day} de {meses_es[fecha_seleccionada.month]} de {fecha_seleccionada.year}"
    dia_nombre = dias_semana_es[fecha_seleccionada.weekday()]

    context = {
        "user_info": user_info,
        "hoy": hoy,
        "fecha_seleccionada": fecha_seleccionada,
        "fecha_iso": fecha_seleccionada.strftime("%Y-%m-%d"),
        "fecha_formateada": fecha_formateada,
        "dia_nombre": dia_nombre,
        "salas": salas,
        "estudiantes": estudiantes,
        "reservas_calendario": reservas_calendario,
        "todas_las_reservas": todas_las_reservas,
        "metricas": metricas,
        "bloques_predefinidos": BLOQUES_PREDEFINIDOS,
        "q_busqueda": q_busqueda,
        "filtro_estado": request.GET.get("filtro_estado", ""),
        "tiene_poderes": True,
    }

    return render(request, "web/admin_dashboard.html", context)


# ==============================================================================
# APIS AJAX PARA RESERVAS Y ADMINISTRACIÓN CON PODERES ESPECIALES
# ==============================================================================

@require_POST
@login_required(login_url="/login/")
def api_reservar(request: HttpRequest) -> JsonResponse:
    """Endpoint AJAX para crear una reserva validando reglas y persistiendo en MongoDB."""
    try:
        if request.content_type == "application/json":
            datos = json.loads(request.body)
        else:
            datos = request.POST

        codigo_estudiante = datos.get("codigo_estudiante", "").strip()
        nombre_sala = datos.get("nombre_sala", "").strip()
        hora_inicio = datos.get("hora_inicio", "").strip()
        hora_fin = datos.get("hora_fin", "").strip()
        fecha_str = datos.get("fecha", "").strip() or None

        # Un estudiante solo reserva a su nombre: se ignora el código que venga en el formulario.
        if not tiene_poderes_especiales(request.user):
            propio = estudiante_del_usuario(request.user)
            if propio is None:
                return JsonResponse({
                    "estado": "RECHAZADA",
                    "mensaje": "Tu usuario no está vinculado a un estudiante. Inicia sesión con tu código y correo.",
                }, status=403)
            codigo_estudiante = propio.codigo_estudiante

        if not codigo_estudiante or not nombre_sala or not hora_inicio or not hora_fin:
            return JsonResponse({
                "estado": "RECHAZADA",
                "mensaje": "Todos los campos (Código estudiante, Sala y Horario) son obligatorios.",
            })

        resultado = reservar_si_es_posible(
            codigo_estudiante=codigo_estudiante,
            nombre_sala=nombre_sala,
            horas=(hora_inicio, hora_fin),
            fecha=fecha_str,
        )

        return JsonResponse(resultado)

    except Exception as e:
        return JsonResponse({
            "estado": "RECHAZADA",
            "mensaje": f"Ocurrió un error al procesar la reserva: {str(e)}",
        }, status=400)


@require_POST
@login_required(login_url="/login/")
def api_editar_reserva(request: HttpRequest) -> JsonResponse:
    """Endpoint exclusivo para administradores con poderes especiales.

    Permite mover fechas, cambiar salas, modificar horarios o cambiar el estado de cualquier reserva.
    """
    if not tiene_poderes_especiales(request.user):
        return JsonResponse({
            "estado": "RECHAZADA",
            "mensaje": "Acción denegada. Solo los administradores con poderes pueden editar reservas.",
        }, status=403)

    try:
        if request.content_type == "application/json":
            datos = json.loads(request.body)
        else:
            datos = request.POST

        reserva_id = datos.get("reserva_id")
        reserva = Reserva.objects.filter(id=reserva_id).first()
        if not reserva:
            return JsonResponse({"estado": "RECHAZADA", "mensaje": "Reserva no encontrada."})

        # Actualizar sala si se proporciona
        nombre_sala = datos.get("nombre_sala")
        if nombre_sala:
            sala = Sala.objects.filter(nombre=nombre_sala).first()
            if sala:
                reserva.sala = sala

        # Actualizar fecha si se proporciona
        nueva_fecha_str = datos.get("fecha")
        if nueva_fecha_str:
            reserva.fecha = datetime.datetime.strptime(nueva_fecha_str, "%Y-%m-%d").date()

        # Actualizar horarios si se proporcionan
        nueva_h_ini = datos.get("hora_inicio")
        nueva_h_fin = datos.get("hora_fin")
        if nueva_h_ini and nueva_h_fin:
            min_ini, min_fin = validar_rango_horario(nueva_h_ini, nueva_h_fin)
            reserva.hora_inicio = minutos_a_time(min_ini)
            reserva.hora_fin = minutos_a_time(min_fin)

        # Actualizar estado si se proporciona
        nuevo_estado = datos.get("estado")
        if nuevo_estado in [Reserva.ESTADO_CONFIRMADA, Reserva.ESTADO_CANCELADA]:
            reserva.estado = nuevo_estado

        reserva.save()

        return JsonResponse({
            "estado": "CONFIRMADA",
            "mensaje": f"Reserva #{reserva.id} actualizada correctamente en MongoDB.",
            "datos": {
                "id": str(reserva.id),
                "sala": reserva.sala.nombre,
                "fecha": str(reserva.fecha),
                "hora_inicio": reserva.hora_inicio.strftime("%H:%M"),
                "hora_fin": reserva.hora_fin.strftime("%H:%M"),
                "estado": reserva.estado,
            },
        })

    except Exception as e:
        return JsonResponse({"estado": "RECHAZADA", "mensaje": f"Error al editar reserva: {str(e)}"}, status=400)


def _datos_reserva(reserva: Reserva) -> dict:
    """Representación JSON de una reserva (la usa la pantalla para actualizar la agenda)."""
    return {
        "id": str(reserva.id),
        "sala": reserva.sala.nombre,
        "fecha": reserva.fecha.strftime("%Y-%m-%d"),
        "hora_inicio": reserva.hora_inicio.strftime("%H:%M"),
        "hora_fin": reserva.hora_fin.strftime("%H:%M"),
        "estado": reserva.estado,
    }


@require_POST
@login_required(login_url="/login/")
def api_modificar_reserva(request: HttpRequest) -> JsonResponse:
    """RES-05 / RES-CU-01: el dueño (o un administrador) cambia fecha y horario de una reserva.

    Entrada (JSON o formulario): ``reserva_id``, ``fecha`` (AAAA-MM-DD),
    ``hora_inicio`` y ``hora_fin`` (HH:MM).

    Respuestas:
      - Aceptada:  {"estado": "CONFIRMADA", "mensaje", "datos": reserva ya modificada}
      - Rechazada por reglas (E1): {"estado": "RECHAZADA", "mensaje": causa,
        "preguntar_mantener": true, "pregunta": "¿Deseas mantenerla?",
        "datos": reserva original sin cambios}. Si el estudiante responde
        "No" (o Esc), la pantalla llama a /api/cancelar/ (RES-RF-03).
      - Ya comenzó (E2) o reserva cancelada: igual, pero "preguntar_mantener": false.
      - Datos mal escritos: estado RECHAZADA con HTTP 400. Sin permiso: HTTP 403.
    """
    try:
        datos = json.loads(request.body) if request.content_type == "application/json" else request.POST
    except ValueError:
        datos = None
    if not hasattr(datos, "get"):
        return JsonResponse({"estado": "RECHAZADA", "mensaje": "La solicitud no tiene un formato válido."}, status=400)

    reserva_id = str(datos.get("reserva_id", "")).strip()
    try:
        reserva = Reserva.objects.select_related("estudiante", "sala").filter(id=reserva_id).first() if reserva_id else None
    except (ValueError, ValidationError):  # id con formato inválido
        reserva = None
    if not reserva:
        return JsonResponse({"estado": "RECHAZADA", "mensaje": "Reserva no encontrada."}, status=404)

    if not (tiene_poderes_especiales(request.user) or es_duenio_de_reserva(request.user, reserva)):
        return JsonResponse({
            "estado": "RECHAZADA",
            "mensaje": "Solo el estudiante dueño de la reserva o un administrador puede modificarla.",
        }, status=403)

    try:
        fecha = datetime.datetime.strptime(str(datos.get("fecha", "")).strip(), "%Y-%m-%d").date()
        hora_inicio, hora_fin = parsear_horas((str(datos.get("hora_inicio", "")), str(datos.get("hora_fin", ""))))
    except ValueError as e:
        return JsonResponse({
            "estado": "RECHAZADA",
            "mensaje": f"Datos inválidos: usa fecha AAAA-MM-DD y horas HH:MM, con fin posterior al inicio. ({e})",
        }, status=400)

    try:
        reserva = modificar_reserva_si_esta_disponible(
            reserva=reserva, fecha=fecha, hora_inicio=hora_inicio, hora_fin=hora_fin,
        )
    except ReservaRechazada as e:
        reserva.refresh_from_db()  # lo que quedó guardado: la reserva original
        preguntar = not isinstance(e, ReservaYaComenzo) and reserva.estado == Reserva.ESTADO_CONFIRMADA
        respuesta = {
            "estado": "RECHAZADA",
            "mensaje": str(e),
            "preguntar_mantener": preguntar,
            "datos": _datos_reserva(reserva),
        }
        if preguntar:
            respuesta["pregunta"] = "¿Deseas mantenerla?"
        return JsonResponse(respuesta)

    return JsonResponse({
        "estado": "CONFIRMADA",
        "mensaje": (
            f"Reserva modificada: {reserva.sala.nombre}, {reserva.fecha:%d/%m/%Y} "
            f"de {reserva.hora_inicio:%H:%M} a {reserva.hora_fin:%H:%M}."
        ),
        "datos": _datos_reserva(reserva),
    })


@require_POST
@login_required(login_url="/login/")
def api_cancelar_reserva(request: HttpRequest) -> JsonResponse:
    """Endpoint AJAX para cancelar una reserva."""
    try:
        if request.content_type == "application/json":
            datos = json.loads(request.body)
        else:
            datos = request.POST

        reserva_id = datos.get("reserva_id")
        if not reserva_id:
            return JsonResponse({"estado": "RECHAZADA", "mensaje": "ID de reserva no proporcionado."})

        reserva = Reserva.objects.filter(id=reserva_id).first()
        if not reserva:
            return JsonResponse({"estado": "RECHAZADA", "mensaje": "Reserva no encontrada."})

        es_admin = tiene_poderes_especiales(request.user)
        if not es_admin:
            if not es_duenio_de_reserva(request.user, reserva):
                return JsonResponse({
                    "estado": "RECHAZADA",
                    "mensaje": "No tienes permisos para cancelar reservas de otros estudiantes.",
                }, status=403)

        reserva.estado = Reserva.ESTADO_CANCELADA
        reserva.save()

        return JsonResponse({
            "estado": "EXITO",
            "mensaje": f"Reserva en {reserva.sala.nombre} cancelada exitosamente.",
        })

    except Exception as e:
        return JsonResponse({"estado": "RECHAZADA", "mensaje": str(e)}, status=400)


@require_POST
@login_required(login_url="/login/")
def api_eliminar_reserva_definitiva(request: HttpRequest) -> JsonResponse:
    """Endpoint exclusivo para administradores con poderes para borrar definitivamente un registro de reserva."""
    if not tiene_poderes_especiales(request.user):
        return JsonResponse({
            "estado": "RECHAZADA",
            "mensaje": "Acción denegada. Solo los administradores con poderes pueden eliminar registros.",
        }, status=403)

    try:
        if request.content_type == "application/json":
            datos = json.loads(request.body)
        else:
            datos = request.POST

        reserva_id = datos.get("reserva_id")
        reserva = Reserva.objects.filter(id=reserva_id).first()
        if not reserva:
            return JsonResponse({"estado": "RECHAZADA", "mensaje": "Reserva no encontrada."})

        reserva.delete()
        return JsonResponse({
            "estado": "EXITO",
            "mensaje": "Registro de reserva eliminado definitivamente de la base de datos.",
        })
    except Exception as e:
        return JsonResponse({"estado": "RECHAZADA", "mensaje": str(e)}, status=400)


@require_POST
@login_required(login_url="/login/")
def api_toggle_mantenimiento(request: HttpRequest) -> JsonResponse:
    """Endpoint exclusivo para usuarios con poderes especiales para alternar mantenimiento de salas."""
    if not tiene_poderes_especiales(request.user):
        return JsonResponse({
            "estado": "RECHAZADA",
            "mensaje": "Acción denegada. Solo los administradores con poderes especiales pueden modificar salas.",
        }, status=403)

    try:
        if request.content_type == "application/json":
            datos = json.loads(request.body)
        else:
            datos = request.POST

        sala_id = datos.get("sala_id")
        sala = Sala.objects.filter(id=sala_id).first()
        if not sala:
            return JsonResponse({"estado": "RECHAZADA", "mensaje": "Sala no encontrada."})

        sala.en_mantenimiento = not sala.en_mantenimiento
        sala.save()

        estado_texto = "en mantenimiento (deshabilitada)" if sala.en_mantenimiento else "habilitada para reservas"
        return JsonResponse({
            "estado": "EXITO",
            "sala_id": str(sala.id),
            "en_mantenimiento": sala.en_mantenimiento,
            "mensaje": f"La sala '{sala.nombre}' ahora está {estado_texto}.",
        })

    except Exception as e:
        return JsonResponse({"estado": "RECHAZADA", "mensaje": str(e)}, status=400)


@require_POST
@login_required(login_url="/login/")
def api_crear_sala(request: HttpRequest) -> JsonResponse:
    """Endpoint exclusivo para administradores para crear una nueva sala de estudio."""
    if not tiene_poderes_especiales(request.user):
        return JsonResponse({
            "estado": "RECHAZADA",
            "mensaje": "Acción denegada. Solo los administradores con poderes pueden crear salas.",
        }, status=403)

    try:
        if request.content_type == "application/json":
            datos = json.loads(request.body)
        else:
            datos = request.POST

        nombre = datos.get("nombre", "").strip()
        if not nombre:
            return JsonResponse({"estado": "RECHAZADA", "mensaje": "El nombre de la sala es obligatorio."})

        if Sala.objects.filter(nombre__iexact=nombre).exists():
            return JsonResponse({"estado": "RECHAZADA", "mensaje": f"Ya existe una sala con el nombre '{nombre}'."})

        sala = Sala.objects.create(nombre=nombre, en_mantenimiento=False)
        return JsonResponse({
            "estado": "EXITO",
            "mensaje": f"Sala '{sala.nombre}' creada exitosamente en el sistema.",
            "sala_id": str(sala.id),
            "nombre": sala.nombre,
        })
    except Exception as e:
        return JsonResponse({"estado": "RECHAZADA", "mensaje": str(e)}, status=400)