from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Sala, Reserva


@login_required
def home(request):
    salas = Sala.objects.all().order_by('nombre')
    reservas = Reserva.objects.filter(estado=Reserva.ESTADO_CONFIRMADA).order_by('fecha', 'hora_inicio')
    return render(request, 'reservas/home.html', {
        'salas': salas,
        'reservas': reservas,
    })