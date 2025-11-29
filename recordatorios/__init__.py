"""
Sistema de Recordatorios y Notificaciones de APPO
==================================================

Este módulo centraliza todas las notificaciones por WhatsApp.

Uso básico:
-----------
    from recordatorios import notificar_cita_agendada, notificar_cita_cancelada
    
    # Cuando se agenda una cita
    notificar_cita_agendada(reserva)
    
    # Cuando se cancela una cita
    notificar_cita_cancelada(reserva, motivo="Cliente solicitó cancelación")
    
    # Cuando se reprograma una cita
    notificar_cita_reprogramada(reserva, fecha_anterior, hora_anterior)

Uso avanzado:
-------------
    from recordatorios.whatsapp_service import notificacion_whatsapp
    
    # Verificar configuración
    config = notificacion_whatsapp.verificar_configuracion()
    print(config)
    
    # Enviar recordatorio manual
    notificacion_whatsapp.enviar_recordatorio_dia_antes(reserva)

Notas:
------
- Las notificaciones se envían automáticamente via signals al crear/modificar reservas
- No es necesario llamar manualmente a estas funciones en la mayoría de los casos
- Las señales detectan automáticamente: creación, cancelación y reprogramación
"""

# Exponer las funciones principales para uso conveniente
from .whatsapp_service import (
    notificar_cita_agendada,
    notificar_cita_cancelada,
    notificar_cita_reprogramada,
    notificacion_whatsapp,
)

__all__ = [
    'notificar_cita_agendada',
    'notificar_cita_cancelada', 
    'notificar_cita_reprogramada',
    'notificacion_whatsapp',
]


