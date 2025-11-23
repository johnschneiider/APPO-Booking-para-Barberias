"""
Servicio de fidelización por WhatsApp con sistema de loop
"""
import logging
import threading
import time
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from clientes.whatsapp_service import whatsapp_service

logger = logging.getLogger(__name__)


class MensajeFidelizacionService:
    """Servicio para gestionar mensajes de fidelización"""
    
    @staticmethod
    def crear_mensaje_confirmacion(reserva):
        """
        Crea un mensaje de confirmación inmediato cuando se crea una reserva
        """
        from fidelizacion.models import MensajeFidelizacion, TipoMensaje, EstadoMensaje
        
        if not reserva.cliente.telefono:
            logger.warning(f"Cliente {reserva.cliente.username} no tiene teléfono configurado")
            return None
        
        # Formatear mensaje de confirmación
        fecha_formateada = reserva.fecha.strftime('%d/%m/%Y')
        hora_formateada = reserva.hora_inicio.strftime('%H:%M')
        negocio_nombre = reserva.peluquero.nombre
        
        # Obtener nombre del servicio
        if reserva.servicio:
            try:
                servicio_nombre = reserva.servicio.servicio.nombre
            except AttributeError:
                servicio_nombre = "Servicio general"
        else:
            servicio_nombre = "Servicio general"
        
        profesional_nombre = reserva.profesional.nombre_completo if reserva.profesional else "Profesional asignado"
        
        mensaje = (
            f"✅ *Confirmación de Reserva*\n\n"
            f"Hola {reserva.cliente.get_full_name() or reserva.cliente.username},\n\n"
            f"Tu reserva ha sido confirmada:\n\n"
            f"📍 *Negocio:* {negocio_nombre}\n"
            f"👤 *Profesional:* {profesional_nombre}\n"
            f"✂️ *Servicio:* {servicio_nombre}\n"
            f"📅 *Fecha:* {fecha_formateada}\n"
            f"🕐 *Hora:* {hora_formateada}\n\n"
            f"¡Te esperamos!"
        )
        
        # Crear mensaje programado para enviar inmediatamente
        mensaje_obj = MensajeFidelizacion.objects.create(
            tipo=TipoMensaje.CONFIRMACION_RESERVA,
            estado=EstadoMensaje.PROGRAMADO,
            destinatario=reserva.cliente,
            reserva=reserva,
            fecha_programada=timezone.now(),  # Enviar inmediatamente
            mensaje=mensaje
        )
        
        logger.info(f"Mensaje de confirmación creado para reserva {reserva.id}")
        return mensaje_obj
    
    @staticmethod
    def crear_recordatorio_24h(reserva):
        """
        Crea un recordatorio programado para 24 horas antes de la cita
        """
        from fidelizacion.models import MensajeFidelizacion, TipoMensaje, EstadoMensaje
        
        if not reserva.cliente.telefono:
            return None
        
        # Calcular fecha y hora de la cita
        fecha_hora_cita = timezone.make_aware(
            datetime.combine(reserva.fecha, reserva.hora_inicio)
        )
        
        # Programar para 24 horas antes
        fecha_programada = fecha_hora_cita - timedelta(hours=24)
        
        # Si ya pasó el momento de enviar, no crear el recordatorio
        if fecha_programada < timezone.now():
            logger.warning(f"No se puede programar recordatorio 24h para reserva {reserva.id} - ya pasó el momento")
            return None
        
        # Formatear mensaje
        fecha_formateada = reserva.fecha.strftime('%d/%m/%Y')
        hora_formateada = reserva.hora_inicio.strftime('%H:%M')
        negocio_nombre = reserva.peluquero.nombre
        
        mensaje = (
            f"🔔 *Recordatorio de Cita*\n\n"
            f"Hola {reserva.cliente.get_full_name() or reserva.cliente.username},\n\n"
            f"Te recordamos que tienes una cita mañana:\n\n"
            f"📍 *Negocio:* {negocio_nombre}\n"
            f"📅 *Fecha:* {fecha_formateada}\n"
            f"🕐 *Hora:* {hora_formateada}\n\n"
            f"¡No olvides asistir!"
        )
        
        mensaje_obj = MensajeFidelizacion.objects.create(
            tipo=TipoMensaje.RECORDATORIO_24H,
            estado=EstadoMensaje.PROGRAMADO,
            destinatario=reserva.cliente,
            reserva=reserva,
            fecha_programada=fecha_programada,
            mensaje=mensaje
        )
        
        logger.info(f"Recordatorio 24h programado para reserva {reserva.id} - {fecha_programada}")
        return mensaje_obj
    
    @staticmethod
    def crear_recordatorio_1h(reserva):
        """
        Crea un recordatorio programado para 1 hora antes de la cita
        """
        from fidelizacion.models import MensajeFidelizacion, TipoMensaje, EstadoMensaje
        
        if not reserva.cliente.telefono:
            return None
        
        # Calcular fecha y hora de la cita
        fecha_hora_cita = timezone.make_aware(
            datetime.combine(reserva.fecha, reserva.hora_inicio)
        )
        
        # Programar para 1 hora antes
        fecha_programada = fecha_hora_cita - timedelta(hours=1)
        
        # Si ya pasó el momento de enviar, no crear el recordatorio
        if fecha_programada < timezone.now():
            logger.warning(f"No se puede programar recordatorio 1h para reserva {reserva.id} - ya pasó el momento")
            return None
        
        # Formatear mensaje
        fecha_formateada = reserva.fecha.strftime('%d/%m/%Y')
        hora_formateada = reserva.hora_inicio.strftime('%H:%M')
        negocio_nombre = reserva.peluquero.nombre
        
        mensaje = (
            f"⏰ *Recordatorio de Cita*\n\n"
            f"Hola {reserva.cliente.get_full_name() or reserva.cliente.username},\n\n"
            f"Tu cita es en 1 hora:\n\n"
            f"📍 *Negocio:* {negocio_nombre}\n"
            f"📅 *Fecha:* {fecha_formateada}\n"
            f"🕐 *Hora:* {hora_formateada}\n\n"
            f"¡Nos vemos pronto!"
        )
        
        mensaje_obj = MensajeFidelizacion.objects.create(
            tipo=TipoMensaje.RECORDATORIO_1H,
            estado=EstadoMensaje.PROGRAMADO,
            destinatario=reserva.cliente,
            reserva=reserva,
            fecha_programada=fecha_programada,
            mensaje=mensaje
        )
        
        logger.info(f"Recordatorio 1h programado para reserva {reserva.id} - {fecha_programada}")
        return mensaje_obj
    
    @staticmethod
    def cancelar_mensajes_reserva(reserva):
        """
        Cancela todos los mensajes pendientes de una reserva
        """
        from fidelizacion.models import MensajeFidelizacion, EstadoMensaje
        
        mensajes = MensajeFidelizacion.objects.filter(
            reserva=reserva,
            estado__in=[EstadoMensaje.PENDIENTE, EstadoMensaje.PROGRAMADO]
        )
        
        count = mensajes.update(estado=EstadoMensaje.CANCELADO)
        logger.info(f"Cancelados {count} mensajes para reserva {reserva.id}")
        return count


class MensajeLoopService:
    """
    Servicio que ejecuta un loop en un thread separado para procesar mensajes programados
    """
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.check_interval = 60  # Revisar cada 60 segundos
    
    def start(self):
        """Inicia el loop de procesamiento"""
        if self.running:
            logger.warning("El loop de mensajes ya está corriendo")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        logger.info("Loop de procesamiento de mensajes iniciado")
    
    def stop(self):
        """Detiene el loop de procesamiento"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Loop de procesamiento de mensajes detenido")
    
    def _loop(self):
        """Loop principal que procesa mensajes programados"""
        logger.info("Iniciando loop de procesamiento de mensajes...")
        
        while self.running:
            try:
                self._procesar_mensajes()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error en loop de mensajes: {e}", exc_info=True)
                time.sleep(self.check_interval)
    
    def _procesar_mensajes(self):
        """Procesa los mensajes que están listos para enviar"""
        from fidelizacion.models import MensajeFidelizacion, EstadoMensaje
        
        try:
            ahora = timezone.now()
            
            # Obtener mensajes programados que ya deben enviarse
            mensajes_pendientes = MensajeFidelizacion.objects.filter(
                estado=EstadoMensaje.PROGRAMADO,
                fecha_programada__lte=ahora
            ).select_related('destinatario', 'reserva')[:10]  # Procesar máximo 10 a la vez
        except Exception as e:
            # Si hay error de base de datos (tabla no existe, columna no existe, etc.)
            # simplemente retornar sin procesar
            logger.warning(f"No se pueden procesar mensajes (posible problema de migraciones): {e}")
            return
        
        if not mensajes_pendientes:
            return
        
        for mensaje in mensajes_pendientes:
            try:
                # Verificar que la reserva aún existe y está activa
                if mensaje.reserva:
                    if mensaje.reserva.estado in ['cancelado', 'inasistencia']:
                        mensaje.cancelar()
                        logger.info(f"Mensaje {mensaje.id} cancelado - reserva en estado {mensaje.reserva.estado}")
                        continue
                
                # Enviar mensaje
                if self._enviar_mensaje(mensaje):
                    mensaje.marcar_enviado()
                    logger.info(f"Mensaje {mensaje.id} enviado exitosamente")
                else:
                    mensaje.marcar_fallido("Error al enviar mensaje")
                    logger.warning(f"Error al enviar mensaje {mensaje.id}")
                    
            except Exception as e:
                logger.error(f"Error procesando mensaje {mensaje.id}: {e}", exc_info=True)
                mensaje.marcar_fallido(str(e))
    
    def _enviar_mensaje(self, mensaje):
        """Envía un mensaje usando el servicio de WhatsApp"""
        try:
            if not whatsapp_service.is_enabled():
                logger.warning("WhatsApp no está habilitado")
                return False
            
            if not mensaje.destinatario.telefono:
                logger.warning(f"Cliente {mensaje.destinatario.username} no tiene teléfono")
                return False
            
            # Enviar mensaje personalizado
            resultado = whatsapp_service.send_custom_message(
                mensaje.destinatario.telefono,
                mensaje.mensaje
            )
            
            return resultado
            
        except Exception as e:
            logger.error(f"Error enviando mensaje {mensaje.id}: {e}", exc_info=True)
            return False

