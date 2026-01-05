"""
Vistas para editar y gestionar reservas desde WhatsApp
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .models import Reserva
from .editar_reserva_forms import EditarReservaForm
import logging

logger = logging.getLogger(__name__)

@login_required
def editar_reserva(request, reserva_id):
    """
    Vista para editar una reserva desde el enlace de WhatsApp
    """
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente=request.user)
    
    # Verificar que la reserva no esté completada o cancelada
    if reserva.estado in ['completado', 'cancelado']:
        messages.error(request, 'No se puede editar una reserva que ya está completada o cancelada.')
        return redirect('clientes:mis_reservas')
    
    # Verificar restricciones de tiempo para cancelación
    ahora = timezone.now()
    hora_cita = timezone.datetime.combine(reserva.fecha, reserva.hora_inicio)
    tiempo_restante = hora_cita - ahora
    
    puede_cancelar = tiempo_restante.total_seconds() > 3600  # Más de 1 hora
    puede_reagendar = tiempo_restante.total_seconds() > 1800  # Más de 30 minutos
    
    if request.method == 'POST':
        form = EditarReservaForm(request.POST, instance=reserva)
        if form.is_valid():
            # Verificar restricciones antes de guardar
            nueva_fecha = form.cleaned_data['fecha']
            nueva_hora = form.cleaned_data['hora_inicio']
            
            # Verificar que la nueva fecha/hora no sea en el pasado
            nueva_fecha_hora = timezone.datetime.combine(nueva_fecha, nueva_hora)
            if nueva_fecha_hora < ahora:
                messages.error(request, 'No puedes reagendar para una fecha/hora en el pasado.')
                return render(request, 'clientes/editar_reserva.html', {
                    'form': form,
                    'reserva': reserva,
                    'puede_cancelar': puede_cancelar,
                    'puede_reagendar': puede_reagendar
                })
            
            # Guardar cambios
            form.save()
            messages.success(request, 'Reserva actualizada exitosamente.')
            return redirect('clientes:mis_reservas')
    else:
        form = EditarReservaForm(instance=reserva)
    
    return render(request, 'clientes/editar_reserva.html', {
        'form': form,
        'reserva': reserva,
        'puede_cancelar': puede_cancelar,
        'puede_reagendar': puede_reagendar,
        'tiempo_restante': tiempo_restante
    })

@login_required
@require_http_methods(["POST"])
def cancelar_reserva_desde_whatsapp(request, reserva_id):
    """
    Cancela una reserva desde el enlace de WhatsApp
    """
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente=request.user)
    
    # Verificar restricciones de tiempo
    ahora = timezone.now()
    hora_cita = timezone.datetime.combine(reserva.fecha, reserva.hora_inicio)
    tiempo_restante = hora_cita - ahora
    
    if tiempo_restante.total_seconds() <= 3600:  # Menos de 1 hora
        return JsonResponse({
            'success': False,
            'error': 'No se puede cancelar con menos de 1 hora de anticipación.'
        })
    
    if reserva.estado in ['completado', 'cancelado']:
        return JsonResponse({
            'success': False,
            'error': 'No se puede cancelar una reserva que ya está completada o cancelada.'
        })
    
    try:
        with transaction.atomic():
            # Cancelar la reserva (esto actualiza notas/validaciones y disparará la señal
            # de recordatorios para enviar WhatsApp SIN duplicados)
            reserva.cancelar(
                motivo="Cancelada por el cliente desde WhatsApp",
                cancelado_por="cliente"
            )
            
            logger.info(f"Reserva {reserva_id} cancelada por {request.user.username}")
            
            return JsonResponse({
                'success': True,
                'message': 'Reserva cancelada exitosamente.'
            })
            
    except Exception as e:
        logger.error(f"Error cancelando reserva {reserva_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Error interno del servidor.'
        })

@login_required
def vista_reserva_movil(request, reserva_id):
    """
    Vista optimizada para móviles desde WhatsApp
    """
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente=request.user)
    
    # Verificar restricciones de tiempo
    ahora = timezone.now()
    hora_cita = timezone.datetime.combine(reserva.fecha, reserva.hora_inicio)
    tiempo_restante = hora_cita - ahora
    
    puede_cancelar = tiempo_restante.total_seconds() > 3600  # Más de 1 hora
    puede_reagendar = tiempo_restante.total_seconds() > 1800  # Más de 30 minutos
    
    return render(request, 'clientes/vista_reserva_movil.html', {
        'reserva': reserva,
        'puede_cancelar': puede_cancelar,
        'puede_reagendar': puede_reagendar,
        'tiempo_restante': tiempo_restante
    })
