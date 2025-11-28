"""
Señales para el sistema de notificaciones de APPO

Conecta automáticamente las acciones de reservas con las notificaciones WhatsApp:
- Cita agendada → Notificación de confirmación
- Cita cancelada → Notificación de cancelación  
- Cita reprogramada → Notificación de reprogramación

Uso:
    Las señales se conectan automáticamente al cargar la app.
    No requiere configuración adicional.
"""

from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
import logging

logger = logging.getLogger('recordatorios.signals')

# Variable para almacenar el estado anterior de las reservas
_reservas_estado_anterior = {}


def get_reserva_model():
    """Obtiene el modelo Reserva de manera segura para evitar imports circulares"""
    try:
        from clientes.models import Reserva
        return Reserva
    except ImportError:
        logger.warning("No se pudo importar el modelo Reserva")
        return None


def get_whatsapp_service():
    """Obtiene el servicio de WhatsApp de manera segura"""
    try:
        from .whatsapp_service import notificacion_whatsapp
        return notificacion_whatsapp
    except ImportError as e:
        logger.error(f"No se pudo importar el servicio de WhatsApp: {e}")
        return None


# =============================================================================
# SEÑALES PARA RESERVAS
# =============================================================================

@receiver(pre_save, sender='clientes.Reserva')
def guardar_estado_anterior_reserva(sender, instance, **kwargs):
    """
    Guarda el estado anterior de la reserva antes de guardar.
    Esto permite detectar cambios en fecha/hora para reprogramaciones.
    """
    if instance.pk:
        try:
            Reserva = get_reserva_model()
            if Reserva:
                reserva_anterior = Reserva.objects.filter(pk=instance.pk).first()
                if reserva_anterior:
                    _reservas_estado_anterior[instance.pk] = {
                        'fecha': reserva_anterior.fecha,
                        'hora_inicio': reserva_anterior.hora_inicio,
                        'hora_fin': reserva_anterior.hora_fin,
                        'estado': reserva_anterior.estado,
                    }
        except Exception as e:
            logger.error(f"Error guardando estado anterior de reserva: {e}")


@receiver(post_save, sender='clientes.Reserva')
def manejar_cambios_reserva(sender, instance, created, **kwargs):
    """
    Maneja las notificaciones cuando se crea o modifica una reserva.
    
    Detecta:
    - Nueva reserva → Notifica cita agendada
    - Cambio de fecha/hora → Notifica reprogramación
    - Cambio de estado a 'cancelado' → Notifica cancelación
    """
    whatsapp = get_whatsapp_service()
    if not whatsapp:
        logger.warning("Servicio WhatsApp no disponible")
        return
    
    try:
        if created:
            # Nueva reserva - Notificar cita agendada
            _notificar_cita_agendada(instance, whatsapp)
        else:
            # Reserva modificada - Verificar qué cambió
            _procesar_modificacion_reserva(instance, whatsapp)
            
    except Exception as e:
        logger.error(f"Error procesando cambios en reserva {instance.id}: {e}")
    finally:
        # Limpiar estado anterior
        if instance.pk in _reservas_estado_anterior:
            del _reservas_estado_anterior[instance.pk]


def _notificar_cita_agendada(reserva, whatsapp):
    """Envía notificación de cita agendada"""
    try:
        # Solo notificar si la reserva está en estado válido
        if reserva.estado in ['pendiente', 'confirmado']:
            resultado = whatsapp.notificar_cita_agendada(reserva)
            
            if resultado.get('success'):
                logger.info(f"✅ Notificación de cita agendada enviada - Reserva {reserva.id}")
            else:
                logger.warning(f"⚠️ No se pudo enviar notificación - Reserva {reserva.id}: {resultado.get('error')}")
                
    except Exception as e:
        logger.error(f"Error notificando cita agendada: {e}")


def _procesar_modificacion_reserva(reserva, whatsapp):
    """Procesa las modificaciones de una reserva"""
    estado_anterior = _reservas_estado_anterior.get(reserva.pk, {})
    
    if not estado_anterior:
        return
    
    # Verificar si se canceló
    if reserva.estado == 'cancelado' and estado_anterior.get('estado') != 'cancelado':
        _notificar_cita_cancelada(reserva, whatsapp)
        return
    
    # Verificar si se reprogramó (cambio de fecha u hora)
    fecha_cambio = estado_anterior.get('fecha') != reserva.fecha
    hora_cambio = estado_anterior.get('hora_inicio') != reserva.hora_inicio
    
    if fecha_cambio or hora_cambio:
        # Solo notificar reprogramación si la reserva sigue activa
        if reserva.estado in ['pendiente', 'confirmado']:
            _notificar_cita_reprogramada(
                reserva=reserva,
                fecha_anterior=estado_anterior.get('fecha'),
                hora_anterior=estado_anterior.get('hora_inicio'),
                whatsapp=whatsapp
            )


def _notificar_cita_cancelada(reserva, whatsapp):
    """Envía notificación de cita cancelada"""
    try:
        # Extraer motivo de las notas si existe
        motivo = ""
        if reserva.notas:
            # Buscar el motivo en las notas
            import re
            match = re.search(r'\[Cancelado[^\]]*\]\s*(.+?)(?:\n|$)', reserva.notas)
            if match:
                motivo = match.group(1).strip()
        
        resultado = whatsapp.notificar_cita_cancelada(reserva, motivo)
        
        if resultado.get('success'):
            logger.info(f"✅ Notificación de cancelación enviada - Reserva {reserva.id}")
        else:
            logger.warning(f"⚠️ No se pudo enviar notificación de cancelación - Reserva {reserva.id}")
            
    except Exception as e:
        logger.error(f"Error notificando cita cancelada: {e}")


def _notificar_cita_reprogramada(reserva, fecha_anterior, hora_anterior, whatsapp):
    """Envía notificación de cita reprogramada"""
    try:
        resultado = whatsapp.notificar_cita_reprogramada(
            reserva=reserva,
            fecha_anterior=fecha_anterior,
            hora_anterior=hora_anterior
        )
        
        if resultado.get('success'):
            logger.info(f"✅ Notificación de reprogramación enviada - Reserva {reserva.id}")
        else:
            logger.warning(f"⚠️ No se pudo enviar notificación de reprogramación - Reserva {reserva.id}")
            
    except Exception as e:
        logger.error(f"Error notificando cita reprogramada: {e}")


@receiver(post_delete, sender='clientes.Reserva')
def manejar_eliminacion_reserva(sender, instance, **kwargs):
    """
    Maneja la eliminación de reservas.
    Cancela los recordatorios pendientes asociados.
    """
    try:
        from .models import Recordatorio, EstadoRecordatorio
        
        content_type = ContentType.objects.get_for_model(instance)
        
        # Cancelar recordatorios pendientes
        actualizados = Recordatorio.objects.filter(
            content_type=content_type,
            object_id=instance.id,
            estado=EstadoRecordatorio.PENDIENTE
        ).update(estado=EstadoRecordatorio.CANCELADO)
        
        if actualizados > 0:
            logger.info(f"Cancelados {actualizados} recordatorios para reserva eliminada {instance.id}")
            
    except Exception as e:
        logger.error(f"Error cancelando recordatorios de reserva eliminada: {e}")


# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

def enviar_notificacion_manual(reserva, tipo: str, **kwargs):
    """
    Permite enviar notificaciones manualmente desde otras partes del código.
    
    Args:
        reserva: Objeto Reserva
        tipo: 'agendada', 'cancelada', 'reprogramada'
        **kwargs: Argumentos adicionales según el tipo
        
    Ejemplo:
        from recordatorios.signals import enviar_notificacion_manual
        
        # Notificar cancelación con motivo personalizado
        enviar_notificacion_manual(reserva, 'cancelada', motivo='Cliente no disponible')
    """
    whatsapp = get_whatsapp_service()
    if not whatsapp:
        return {'success': False, 'error': 'Servicio WhatsApp no disponible'}
    
    if tipo == 'agendada':
        return whatsapp.notificar_cita_agendada(reserva)
    elif tipo == 'cancelada':
        return whatsapp.notificar_cita_cancelada(reserva, kwargs.get('motivo', ''))
    elif tipo == 'reprogramada':
        return whatsapp.notificar_cita_reprogramada(
            reserva,
            kwargs.get('fecha_anterior'),
            kwargs.get('hora_anterior')
        )
    else:
        return {'success': False, 'error': f'Tipo de notificación no válido: {tipo}'}


def verificar_conexion_signals():
    """
    Verifica que las señales estén conectadas correctamente.
    Útil para debugging.
    """
    from django.db.models.signals import post_save, pre_save, post_delete
    
    Reserva = get_reserva_model()
    if not Reserva:
        return {'connected': False, 'error': 'Modelo Reserva no encontrado'}
    
    # Verificar señales conectadas
    pre_save_receivers = pre_save.receivers
    post_save_receivers = post_save.receivers
    post_delete_receivers = post_delete.receivers
    
    return {
        'connected': True,
        'reserva_model': str(Reserva),
        'pre_save_count': len([r for r in pre_save_receivers if 'Reserva' in str(r)]),
        'post_save_count': len([r for r in post_save_receivers if 'Reserva' in str(r)]),
        'post_delete_count': len([r for r in post_delete_receivers if 'Reserva' in str(r)]),
        'whatsapp_enabled': get_whatsapp_service() is not None
    }


# =============================================================================
# INICIALIZACIÓN
# =============================================================================

def conectar_senales():
    """
    Conecta las señales al iniciar la aplicación.
    Esta función es llamada automáticamente desde apps.py
    """
    try:
        Reserva = get_reserva_model()
        if Reserva:
            logger.info("✅ Señales de notificaciones conectadas para Reserva")
            return True
        else:
            logger.warning("⚠️ No se pudieron conectar las señales - Modelo Reserva no disponible")
            return False
    except Exception as e:
        logger.error(f"❌ Error conectando señales: {e}")
        return False
