"""
Servicio centralizado de notificaciones WhatsApp para APPO
Toda la lógica de notificaciones WhatsApp se maneja desde aquí.

Uso:
    from recordatorios.whatsapp_service import notificacion_whatsapp
    
    # Notificar nueva cita
    notificacion_whatsapp.notificar_cita_agendada(reserva)
    
    # Notificar cancelación
    notificacion_whatsapp.notificar_cita_cancelada(reserva, motivo="...")
    
    # Notificar reprogramación
    notificacion_whatsapp.notificar_cita_reprogramada(reserva, fecha_anterior, hora_anterior)
"""

import logging
from typing import Dict, Any, Optional
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger('recordatorios.whatsapp')


class NotificacionWhatsApp:
    """
    Servicio centralizado para todas las notificaciones por WhatsApp.
    Maneja el envío de mensajes para citas agendadas, canceladas y reprogramadas.
    """
    
    def __init__(self):
        self.client = None
        self.whatsapp_number = None
        self.enabled = False
        self._inicializar()
    
    def _inicializar(self):
        """Inicializa el cliente de Twilio"""
        try:
            from twilio.rest import Client
            
            account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
            auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
            self.whatsapp_number = getattr(settings, 'TWILIO_WHATSAPP_NUMBER', '')
            
            if account_sid and auth_token:
                self.client = Client(account_sid, auth_token)
                self.enabled = True
                logger.info("✅ Servicio WhatsApp inicializado correctamente")
            else:
                logger.warning("⚠️ Credenciales de Twilio no configuradas")
                
        except ImportError:
            logger.error("❌ Twilio no está instalado. Ejecuta: pip install twilio")
        except Exception as e:
            logger.error(f"❌ Error inicializando WhatsApp: {e}")
    
    def _formatear_telefono(self, telefono: str) -> str:
        """
        Formatea el número de teléfono para WhatsApp.
        Agrega código de país +57 (Colombia) si no lo tiene.
        """
        import re
        
        if not telefono:
            return ""
        
        # Limpiar caracteres no numéricos excepto +
        limpio = re.sub(r'[^\d+]', '', str(telefono))
        
        # Agregar código de país si no lo tiene
        if not limpio.startswith('+'):
            if limpio.startswith('57'):
                limpio = '+' + limpio
            elif limpio.startswith('0'):
                limpio = '+57' + limpio[1:]
            else:
                limpio = '+57' + limpio
        
        return limpio
    
    def _enviar_mensaje(self, telefono: str, mensaje: str) -> Dict[str, Any]:
        """
        Envía un mensaje de WhatsApp.
        
        Args:
            telefono: Número de teléfono del destinatario
            mensaje: Texto del mensaje
            
        Returns:
            Dict con el resultado del envío
        """
        if not self.enabled:
            logger.warning("WhatsApp no está habilitado")
            return {'success': False, 'error': 'WhatsApp no configurado'}
        
        if not telefono:
            logger.warning("No se proporcionó número de teléfono")
            return {'success': False, 'error': 'Teléfono no proporcionado'}
        
        try:
            telefono_formateado = self._formatear_telefono(telefono)
            
            message = self.client.messages.create(
                from_=f'whatsapp:{self.whatsapp_number}',
                body=mensaje,
                to=f'whatsapp:{telefono_formateado}'
            )
            
            logger.info(f"✅ Mensaje enviado a {telefono_formateado} - SID: {message.sid}")
            
            return {
                'success': True,
                'message_id': message.sid,
                'status': message.status,
                'to': telefono_formateado
            }
            
        except Exception as e:
            logger.error(f"❌ Error enviando WhatsApp a {telefono}: {e}")
            return {'success': False, 'error': str(e)}
    
    # =========================================================================
    # NOTIFICACIONES DE CITAS
    # =========================================================================
    
    def notificar_cita_agendada(self, reserva) -> Dict[str, Any]:
        """
        Notifica al cliente que su cita ha sido agendada exitosamente.
        
        Args:
            reserva: Objeto Reserva con los datos de la cita
            
        Returns:
            Dict con el resultado del envío
        """
        try:
            cliente = reserva.cliente
            telefono = getattr(cliente, 'telefono', None)
            
            if not telefono:
                logger.warning(f"Cliente {cliente.username} no tiene teléfono")
                return {'success': False, 'error': 'Cliente sin teléfono'}
            
            # Formatear datos
            nombre = cliente.get_full_name() or cliente.username
            fecha = reserva.fecha.strftime('%d de %B de %Y')
            hora = reserva.hora_inicio.strftime('%H:%M')
            negocio = reserva.peluquero.nombre
            servicio = reserva.servicio.servicio.nombre if reserva.servicio else "Servicio"
            profesional = reserva.profesional.nombre_completo if reserva.profesional else negocio
            
            mensaje = f"""🎉 ¡Hola {nombre}!

¡Tu cita ha sido agendada con éxito! ✨

📅 *Fecha:* {fecha}
🕐 *Hora:* {hora}
💇 *Profesional:* {profesional}
💄 *Servicio:* {servicio}
📍 *Lugar:* {negocio}

Te enviaremos un recordatorio antes de tu cita.

¡Te esperamos! 💖

_APPO - Tu agenda de belleza_"""
            
            resultado = self._enviar_mensaje(telefono, mensaje)
            
            # Registrar en historial
            self._registrar_notificacion(
                reserva=reserva,
                tipo='cita_agendada',
                resultado=resultado
            )
            
            return resultado
            
        except Exception as e:
            logger.error(f"Error notificando cita agendada: {e}")
            return {'success': False, 'error': str(e)}
    
    def notificar_cita_cancelada(self, reserva, motivo: str = "") -> Dict[str, Any]:
        """
        Notifica al cliente que su cita ha sido cancelada.
        
        Args:
            reserva: Objeto Reserva con los datos de la cita
            motivo: Motivo de la cancelación (opcional)
            
        Returns:
            Dict con el resultado del envío
        """
        try:
            cliente = reserva.cliente
            telefono = getattr(cliente, 'telefono', None)
            
            if not telefono:
                logger.warning(f"Cliente {cliente.username} no tiene teléfono")
                return {'success': False, 'error': 'Cliente sin teléfono'}
            
            # Formatear datos
            nombre = cliente.get_full_name() or cliente.username
            fecha = reserva.fecha.strftime('%d de %B de %Y')
            hora = reserva.hora_inicio.strftime('%H:%M')
            negocio = reserva.peluquero.nombre
            motivo_texto = motivo if motivo else "No especificado"
            
            mensaje = f"""😔 Hola {nombre}

Tu cita ha sido cancelada:

📅 *Fecha:* {fecha}
🕐 *Hora:* {hora}
📍 *Lugar:* {negocio}

📝 *Motivo:* {motivo_texto}

Si deseas reagendar tu cita, puedes hacerlo desde la app.

¡Esperamos verte pronto! 💖

_APPO - Tu agenda de belleza_"""
            
            resultado = self._enviar_mensaje(telefono, mensaje)
            
            # Registrar en historial
            self._registrar_notificacion(
                reserva=reserva,
                tipo='cita_cancelada',
                resultado=resultado,
                extras={'motivo': motivo}
            )
            
            return resultado
            
        except Exception as e:
            logger.error(f"Error notificando cita cancelada: {e}")
            return {'success': False, 'error': str(e)}
    
    def notificar_cita_reprogramada(
        self, 
        reserva, 
        fecha_anterior, 
        hora_anterior
    ) -> Dict[str, Any]:
        """
        Notifica al cliente que su cita ha sido reprogramada.
        
        Args:
            reserva: Objeto Reserva con los nuevos datos
            fecha_anterior: Fecha original de la cita
            hora_anterior: Hora original de la cita
            
        Returns:
            Dict con el resultado del envío
        """
        try:
            cliente = reserva.cliente
            telefono = getattr(cliente, 'telefono', None)
            
            if not telefono:
                logger.warning(f"Cliente {cliente.username} no tiene teléfono")
                return {'success': False, 'error': 'Cliente sin teléfono'}
            
            # Formatear datos
            nombre = cliente.get_full_name() or cliente.username
            
            # Fecha/hora anterior
            fecha_ant_str = fecha_anterior.strftime('%d de %B de %Y')
            hora_ant_str = hora_anterior.strftime('%H:%M')
            
            # Nueva fecha/hora
            fecha_nueva = reserva.fecha.strftime('%d de %B de %Y')
            hora_nueva = reserva.hora_inicio.strftime('%H:%M')
            
            negocio = reserva.peluquero.nombre
            profesional = reserva.profesional.nombre_completo if reserva.profesional else negocio
            
            mensaje = f"""📅 ¡Hola {nombre}!

Tu cita ha sido reprogramada:

❌ *Fecha anterior:* {fecha_ant_str} a las {hora_ant_str}

✅ *Nueva fecha:* {fecha_nueva}
🕐 *Nueva hora:* {hora_nueva}
💇 *Profesional:* {profesional}
📍 *Lugar:* {negocio}

Te enviaremos un recordatorio antes de tu nueva cita.

¡Te esperamos! ✨

_APPO - Tu agenda de belleza_"""
            
            resultado = self._enviar_mensaje(telefono, mensaje)
            
            # Registrar en historial
            self._registrar_notificacion(
                reserva=reserva,
                tipo='cita_reprogramada',
                resultado=resultado,
                extras={
                    'fecha_anterior': str(fecha_anterior),
                    'hora_anterior': str(hora_anterior)
                }
            )
            
            return resultado
            
        except Exception as e:
            logger.error(f"Error notificando cita reprogramada: {e}")
            return {'success': False, 'error': str(e)}
    
    # =========================================================================
    # RECORDATORIOS
    # =========================================================================
    
    def enviar_recordatorio_dia_antes(self, reserva) -> Dict[str, Any]:
        """Envía recordatorio 24 horas antes de la cita"""
        try:
            cliente = reserva.cliente
            telefono = getattr(cliente, 'telefono', None)
            
            if not telefono:
                return {'success': False, 'error': 'Cliente sin teléfono'}
            
            nombre = cliente.get_full_name() or cliente.username
            fecha = reserva.fecha.strftime('%d de %B de %Y')
            hora = reserva.hora_inicio.strftime('%H:%M')
            negocio = reserva.peluquero.nombre
            direccion = getattr(reserva.peluquero, 'direccion', 'Ver en la app')
            
            mensaje = f"""⏰ ¡Recordatorio!

Hola {nombre}, mañana tienes tu cita 💄

📅 *Fecha:* {fecha}
🕐 *Hora:* {hora}
📍 *Lugar:* {negocio}
🗺️ *Dirección:* {direccion}

¡No olvides llegar puntual! Te esperamos ✨

_APPO - Tu agenda de belleza_"""
            
            return self._enviar_mensaje(telefono, mensaje)
            
        except Exception as e:
            logger.error(f"Error enviando recordatorio día antes: {e}")
            return {'success': False, 'error': str(e)}
    
    def enviar_recordatorio_horas_antes(self, reserva, horas: int = 3) -> Dict[str, Any]:
        """Envía recordatorio N horas antes de la cita"""
        try:
            cliente = reserva.cliente
            telefono = getattr(cliente, 'telefono', None)
            
            if not telefono:
                return {'success': False, 'error': 'Cliente sin teléfono'}
            
            nombre = cliente.get_full_name() or cliente.username
            hora = reserva.hora_inicio.strftime('%H:%M')
            negocio = reserva.peluquero.nombre
            direccion = getattr(reserva.peluquero, 'direccion', 'Ver en la app')
            
            mensaje = f"""⏰ ¡Último recordatorio!

Hola {nombre}, en {horas} horas tienes tu cita 💄

🕐 *Hora:* {hora}
📍 *Lugar:* {negocio}
🗺️ *Dirección:* {direccion}

¡Prepárate para verte increíble! Te esperamos ✨

_APPO - Tu agenda de belleza_"""
            
            return self._enviar_mensaje(telefono, mensaje)
            
        except Exception as e:
            logger.error(f"Error enviando recordatorio {horas}h antes: {e}")
            return {'success': False, 'error': str(e)}
    
    # =========================================================================
    # UTILIDADES
    # =========================================================================
    
    def _registrar_notificacion(
        self, 
        reserva, 
        tipo: str, 
        resultado: Dict[str, Any],
        extras: Dict[str, Any] = None
    ):
        """
        Registra la notificación en el historial.
        """
        try:
            from .models import Recordatorio, HistorialRecordatorio, TipoRecordatorio, CanalNotificacion
            from django.contrib.contenttypes.models import ContentType
            
            # Mapear tipo a TipoRecordatorio
            tipo_map = {
                'cita_agendada': TipoRecordatorio.RESERVA_CONFIRMADA,
                'cita_cancelada': TipoRecordatorio.RESERVA_CANCELADA,
                'cita_reprogramada': TipoRecordatorio.RESERVA_REAGENDADA,
            }
            
            tipo_recordatorio = tipo_map.get(tipo, TipoRecordatorio.CUSTOM)
            
            # Crear recordatorio
            recordatorio = Recordatorio.objects.create(
                tipo=tipo_recordatorio,
                destinatario=reserva.cliente,
                asunto=f"Notificación: {tipo.replace('_', ' ').title()}",
                mensaje=f"Notificación WhatsApp para reserva {reserva.id}",
                fecha_programada=timezone.now(),
                canales_habilitados=['whatsapp'],
                content_type=ContentType.objects.get_for_model(reserva),
                object_id=reserva.id,
                prioridad=1
            )
            
            # Marcar como enviado o fallido
            if resultado.get('success'):
                recordatorio.marcar_enviado('whatsapp')
            else:
                recordatorio.marcar_fallido('whatsapp', resultado.get('error', ''))
            
            # Registrar en historial
            HistorialRecordatorio.objects.create(
                recordatorio=recordatorio,
                accion='enviado' if resultado.get('success') else 'fallido',
                canal=CanalNotificacion.WHATSAPP,
                detalles={
                    'tipo_notificacion': tipo,
                    'resultado': resultado,
                    'extras': extras or {}
                }
            )
            
        except Exception as e:
            logger.error(f"Error registrando notificación: {e}")
    
    def verificar_configuracion(self) -> Dict[str, Any]:
        """
        Verifica el estado de la configuración de WhatsApp.
        Útil para debugging.
        """
        return {
            'enabled': self.enabled,
            'has_client': self.client is not None,
            'whatsapp_number': self.whatsapp_number[:6] + '****' if self.whatsapp_number else None,
            'twilio_configured': bool(getattr(settings, 'TWILIO_ACCOUNT_SID', '')),
        }


# Instancia global del servicio
notificacion_whatsapp = NotificacionWhatsApp()


# =========================================================================
# FUNCIONES DE CONVENIENCIA
# =========================================================================

def notificar_cita_agendada(reserva) -> Dict[str, Any]:
    """Wrapper para notificar cita agendada"""
    return notificacion_whatsapp.notificar_cita_agendada(reserva)


def notificar_cita_cancelada(reserva, motivo: str = "") -> Dict[str, Any]:
    """Wrapper para notificar cita cancelada"""
    return notificacion_whatsapp.notificar_cita_cancelada(reserva, motivo)


def notificar_cita_reprogramada(reserva, fecha_anterior, hora_anterior) -> Dict[str, Any]:
    """Wrapper para notificar cita reprogramada"""
    return notificacion_whatsapp.notificar_cita_reprogramada(
        reserva, fecha_anterior, hora_anterior
    )




