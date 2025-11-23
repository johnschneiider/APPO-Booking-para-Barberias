"""
Señales Django para el sistema de fidelización
"""
import logging
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from clientes.models import Reserva

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Reserva)
def crear_mensajes_fidelizacion(sender, instance, created, **kwargs):
    """
    Cuando se crea una nueva reserva, crea los mensajes de fidelización:
    1. Confirmación inmediata
    2. Recordatorio 24h antes
    3. Recordatorio 1h antes
    """
    if not created:
        return
    
    # Solo procesar reservas en estado pendiente o confirmado
    if instance.estado not in ['pendiente', 'confirmado']:
        return
    
    try:
        from fidelizacion.services import MensajeFidelizacionService
        
        # 1. Crear mensaje de confirmación inmediato
        MensajeFidelizacionService.crear_mensaje_confirmacion(instance)
        
        # 2. Crear recordatorio 24h antes
        MensajeFidelizacionService.crear_recordatorio_24h(instance)
        
        # 3. Crear recordatorio 1h antes
        MensajeFidelizacionService.crear_recordatorio_1h(instance)
        
        logger.info(f"Mensajes de fidelización creados para reserva {instance.id}")
        
    except Exception as e:
        logger.error(f"Error creando mensajes de fidelización para reserva {instance.id}: {e}", exc_info=True)


@receiver(pre_delete, sender=Reserva)
def cancelar_mensajes_al_eliminar_reserva(sender, instance, **kwargs):
    """
    Cuando se elimina una reserva, cancela todos los mensajes pendientes
    """
    try:
        from fidelizacion.services import MensajeFidelizacionService
        MensajeFidelizacionService.cancelar_mensajes_reserva(instance)
    except Exception as e:
        logger.error(f"Error cancelando mensajes al eliminar reserva {instance.id}: {e}", exc_info=True)


@receiver(post_save, sender=Reserva)
def cancelar_mensajes_si_reserva_cancelada(sender, instance, **kwargs):
    """
    Si una reserva se cancela, cancela todos los mensajes pendientes
    """
    if instance.estado == 'cancelado':
        try:
            from fidelizacion.services import MensajeFidelizacionService
            MensajeFidelizacionService.cancelar_mensajes_reserva(instance)
            logger.info(f"Mensajes cancelados para reserva cancelada {instance.id}")
        except Exception as e:
            logger.error(f"Error cancelando mensajes para reserva cancelada {instance.id}: {e}", exc_info=True)

