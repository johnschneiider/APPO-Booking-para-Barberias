"""
Señales para integrar automáticamente el sistema de recordatorios
con reservas y otros eventos del sistema
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from .models import Recordatorio, TipoRecordatorio, EstadoRecordatorio
from .services import servicio_recordatorios
import logging

# Importar modelos para evitar problemas de importación circular
def get_reserva_model():
    """Obtiene el modelo Reserva de manera segura"""
    try:
        from clientes.models import Reserva
        return Reserva
    except ImportError:
        return None

logger = logging.getLogger(__name__)

# Señales para reservas
def conectar_senales():
    """Conecta las señales de manera segura"""
    try:
        Reserva = get_reserva_model()
        if Reserva:
            # Conectar señal de creación/modificación
            post_save.connect(crear_recordatorios_reserva, sender=Reserva, weak=False)
            # Conectar señal de eliminación
            post_delete.connect(eliminar_recordatorios_reserva, sender=Reserva, weak=False)
            logger.info("Señales de recordatorios conectadas exitosamente")
            return True
        else:
            logger.warning("No se pudo obtener el modelo Reserva")
            return False
    except Exception as e:
        logger.error(f"Error conectando señales: {e}")
        return False

def crear_recordatorios_reserva(sender, instance, created, **kwargs):
    """
    Crea recordatorios automáticamente cuando se crea o modifica una reserva
    """
    try:
        if created:
            # Nueva reserva - crear recordatorios
            _crear_recordatorios_para_reserva(instance)
        else:
            # Reserva modificada - actualizar recordatorios existentes
            _actualizar_recordatorios_para_reserva(instance)
            
    except Exception as e:
        logger.error(f"Error creando recordatorios para reserva {instance.id}: {e}")

def eliminar_recordatorios_reserva(sender, instance, **kwargs):
    """
    Elimina recordatorios cuando se elimina una reserva
    """
    try:
        _eliminar_recordatorios_para_reserva(instance)
    except Exception as e:
        logger.error(f"Error eliminando recordatorios para reserva {instance.id}: {e}")

def _crear_recordatorios_para_reserva(reserva):
    """
    Crea recordatorios para una reserva específica
    """
    try:
        # Verificar que la reserva tenga fecha y hora válidas
        if not reserva.fecha or not reserva.hora_inicio:
            logger.warning(f"Reserva {reserva.id} sin fecha/hora válida")
            return
        
        # Crear recordatorio inmediato de confirmación
        servicio_recordatorios.enviar_recordatorio_confirmacion(reserva)
        
        # Crear recordatorio para el día antes
        servicio_recordatorios.enviar_recordatorio_dia_antes(reserva)
        
        # Crear recordatorio para 3 horas antes
        servicio_recordatorios.enviar_recordatorio_tres_horas(reserva)
        
        logger.info(f"Recordatorios creados para reserva {reserva.id}")
        
    except Exception as e:
        logger.error(f"Error creando recordatorios para reserva {reserva.id}: {e}")

def _actualizar_recordatorios_para_reserva(reserva):
    """
    Actualiza recordatorios existentes cuando se modifica una reserva
    """
    try:
        # Buscar recordatorios existentes para esta reserva
        content_type = ContentType.objects.get_for_model(reserva)
        
        recordatorios = Recordatorio.objects.filter(
            content_type=content_type,
            object_id=reserva.id,
            estado__in=[EstadoRecordatorio.PENDIENTE, EstadoRecordatorio.ENVIADO]
        )
        
        if recordatorios.exists():
            # Cancelar recordatorios existentes
            recordatorios.update(estado=EstadoRecordatorio.CANCELADO)
            
            # Crear nuevos recordatorios con la fecha actualizada
            _crear_recordatorios_para_reserva(reserva)
            
            logger.info(f"Recordatorios actualizados para reserva {reserva.id}")
        
    except Exception as e:
        logger.error(f"Error actualizando recordatorios para reserva {reserva.id}: {e}")

def _eliminar_recordatorios_para_reserva(reserva):
    """
    Elimina recordatorios cuando se elimina una reserva
    """
    try:
        content_type = ContentType.objects.get_for_model(reserva)
        
        # Cancelar recordatorios pendientes
        Recordatorio.objects.filter(
            content_type=content_type,
            object_id=reserva.id,
            estado=EstadoRecordatorio.PENDIENTE
        ).update(estado=EstadoRecordatorio.CANCELADO)
        
        logger.info(f"Recordatorios cancelados para reserva eliminada {reserva.id}")
        
    except Exception as e:
        logger.error(f"Error cancelando recordatorios para reserva eliminada {reserva.id}: {e}")

# Señales para suscripciones
@receiver(post_save, sender='suscripciones.Suscripcion')
def crear_recordatorios_suscripcion(sender, instance, created, **kwargs):
    """
    Crea recordatorios para renovaciones de suscripciones
    """
    try:
        if created:
            # Nueva suscripción - crear recordatorio de renovación
            _crear_recordatorio_renovacion_suscripcion(instance)
        else:
            # Suscripción modificada - actualizar recordatorios
            _actualizar_recordatorios_suscripcion(instance)
            
    except Exception as e:
        logger.error(f"Error creando recordatorios para suscripción {instance.id}: {e}")

def _crear_recordatorio_renovacion_suscripcion(suscripcion):
    """
    Crea recordatorio para renovación de suscripción
    """
    try:
        # Calcular fecha de vencimiento
        if hasattr(suscripcion, 'fecha_vencimiento') and suscripcion.fecha_vencimiento:
            fecha_vencimiento = suscripcion.fecha_vencimiento
        else:
            # Por defecto: 30 días desde la creación
            fecha_vencimiento = suscripcion.fecha_creacion + timezone.timedelta(days=30)
        
        # Crear recordatorio 7 días antes del vencimiento
        fecha_recordatorio = fecha_vencimiento - timezone.timedelta(days=7)
        
        if fecha_recordatorio > timezone.now():
            recordatorio = servicio_recordatorios.crear_recordatorio(
                tipo=TipoRecordatorio.SUSCRIPCION_RENOVACION,
                destinatario=suscripcion.usuario,
                fecha_evento=fecha_vencimiento,
                contenido_relacionado=suscripcion,
                canales=['email', 'whatsapp'],
                contexto_template={
                    'usuario': suscripcion.usuario,
                    'suscripcion': suscripcion,
                    'plan': suscripcion.plan,
                    'fecha_vencimiento': fecha_vencimiento.strftime('%d/%m/%Y'),
                    'dias_restantes': 7
                },
                prioridad=2
            )
            
            logger.info(f"Recordatorio de renovación creado para suscripción {suscripcion.id}")
        
    except Exception as e:
        logger.error(f"Error creando recordatorio de renovación: {e}")

def _actualizar_recordatorios_suscripcion(suscripcion):
    """
    Actualiza recordatorios cuando se modifica una suscripción
    """
    try:
        # Buscar recordatorios existentes
        content_type = ContentType.objects.get_for_model(suscripcion)
        
        recordatorios = Recordatorio.objects.filter(
            content_type=content_type,
            object_id=suscripcion.id,
            tipo=TipoRecordatorio.SUSCRIPCION_RENOVACION,
            estado__in=[EstadoRecordatorio.PENDIENTE, EstadoRecordatorio.ENVIADO]
        )
        
        if recordatorios.exists():
            # Cancelar recordatorios existentes
            recordatorios.update(estado=EstadoRecordatorio.CANCELADO)
            
            # Crear nuevos recordatorios
            _crear_recordatorio_renovacion_suscripcion(suscripcion)
            
    except Exception as e:
        logger.error(f"Error actualizando recordatorios de suscripción: {e}")

# Señales para inasistencias (cuando una reserva cambia a estado inasistencia)
@receiver(post_save, sender='clientes.Reserva')
def crear_recordatorio_por_estado_reserva(sender, instance, created, **kwargs):
    """
    Crea recordatorios basados en el estado de la reserva
    """
    try:
        if not created and hasattr(instance, 'estado'):
            # Verificar cambios de estado
            if instance.estado == 'inasistencia':
                _crear_recordatorio_inasistencia(instance)
            elif instance.estado == 'cancelado':
                _crear_recordatorio_cancelacion(instance)
                
    except Exception as e:
        logger.error(f"Error creando recordatorio por estado de reserva {instance.id}: {e}")

def _crear_recordatorio_inasistencia(reserva):
    """
    Crea recordatorio para inasistencia
    """
    try:
        # Enviar recordatorio inmediatamente
        recordatorio = servicio_recordatorios.crear_recordatorio(
            tipo=TipoRecordatorio.INASISTENCIA,
            destinatario=reserva.cliente,
            fecha_evento=timezone.now(),
            contenido_relacionado=reserva,
            canales=['email', 'whatsapp'],
            contexto_template={
                'cliente': reserva.cliente,
                'reserva': reserva,
                'negocio': reserva.peluquero,
                'profesional': reserva.profesional,
                'fecha_inasistencia': timezone.now().strftime('%d/%m/%Y')
            },
            prioridad=1  # Alta prioridad
        )
        
        logger.info(f"Recordatorio de inasistencia creado para {reserva.cliente}")
        
    except Exception as e:
        logger.error(f"Error creando recordatorio de inasistencia: {e}")

def _crear_recordatorio_cancelacion(reserva):
    """
    Crea recordatorio para cancelación de reserva
    """
    try:
        # Enviar recordatorio inmediatamente
        recordatorio = servicio_recordatorios.crear_recordatorio(
            tipo=TipoRecordatorio.RESERVA_CANCELADA,
            destinatario=reserva.cliente,
            fecha_evento=timezone.now(),
            contenido_relacionado=reserva,
            canales=['email', 'whatsapp'],
            contexto_template={
                'cliente': reserva.cliente,
                'reserva': reserva,
                'negocio': reserva.peluquero,
                'profesional': reserva.profesional,
                'fecha_cancelacion': timezone.now().strftime('%d/%m/%Y'),
                'fecha_reserva': reserva.fecha.strftime('%d/%m/%Y'),
                'hora_reserva': reserva.hora_inicio.strftime('%H:%M')
            },
            prioridad=1  # Alta prioridad
        )
        
        logger.info(f"Recordatorio de cancelación creado para {reserva.cliente}")
        
    except Exception as e:
        logger.error(f"Error creando recordatorio de cancelación: {e}")

# La función _crear_recordatorio_cancelacion ya está definida arriba y se usa en crear_recordatorio_por_estado_reserva

# Función para limpiar recordatorios antiguos
def limpiar_recordatorios_antiguos():
    """
    Limpia recordatorios muy antiguos para mantener la base de datos optimizada
    """
    try:
        # Eliminar recordatorios cancelados o fallidos de más de 30 días
        fecha_limite = timezone.now() - timezone.timedelta(days=30)
        
        recordatorios_eliminados = Recordatorio.objects.filter(
            estado__in=[EstadoRecordatorio.CANCELADO, EstadoRecordatorio.FALLIDO],
            fecha_creacion__lt=fecha_limite
        ).delete()
        
        if recordatorios_eliminados[0] > 0:
            logger.info(f"Limpiados {recordatorios_eliminados[0]} recordatorios antiguos")
            
    except Exception as e:
        logger.error(f"Error limpiando recordatorios antiguos: {e}")

# Configurar limpieza automática (puede ser llamada por un cron job)
def tarea_limpieza_recordatorios():
    """
    Tarea programada para limpiar recordatorios antiguos
    """
    limpiar_recordatorios_antiguos()

# Conectar señales cuando se importe el módulo
conectar_senales()
