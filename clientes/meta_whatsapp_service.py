"""
Servicio de WhatsApp usando Meta WhatsApp Business API
Alternativa a Twilio que no requiere registro en Cámara de Comercio
"""

import logging
import requests
import json
from typing import Dict, List, Optional, Any
from django.conf import settings

logger = logging.getLogger(__name__)


class MetaWhatsAppService:
    """
    Servicio principal para WhatsApp usando Meta WhatsApp Business API
    Maneja mensajes, templates y notificaciones
    """
    
    def __init__(self):
        # Obtener configuración de variables de entorno
        self.enabled = getattr(settings, 'META_WHATSAPP_ENABLED', False)
        self.phone_number_id = getattr(settings, 'META_WHATSAPP_PHONE_NUMBER_ID', '')
        self.access_token = getattr(settings, 'META_WHATSAPP_ACCESS_TOKEN', '')
        self.api_version = getattr(settings, 'META_WHATSAPP_API_VERSION', 'v21.0')
        
        # URL base de la API de Meta
        self.api_base_url = f"https://graph.facebook.com/{self.api_version}"
        
        if self.enabled and self.phone_number_id and self.access_token:
            logger.info("Servicio de Meta WhatsApp inicializado correctamente")
        else:
            logger.warning("Meta WhatsApp no está completamente configurado")
    
    def is_enabled(self) -> bool:
        """Verifica si WhatsApp está habilitado y configurado correctamente"""
        return (
            self.enabled and 
            self.phone_number_id and 
            self.access_token
        )
    
    def format_phone_number(self, phone_number: str) -> str:
        """
        Formatea el número de teléfono para WhatsApp
        Elimina espacios, guiones y agrega código de país si es necesario
        """
        import re
        
        # Limpiar el número
        cleaned = re.sub(r'[\s\-\(\)]', '', str(phone_number))
        
        # Si no tiene código de país, agregar +57 (Colombia)
        if not cleaned.startswith('+'):
            if cleaned.startswith('57'):
                cleaned = '+' + cleaned
            elif cleaned.startswith('0'):
                cleaned = '+57' + cleaned[1:]
            else:
                cleaned = '+57' + cleaned
        
        return cleaned
    
    def send_text_message(self, to_phone: str, message: str) -> Dict[str, Any]:
        """
        Envía un mensaje de texto simple usando Meta WhatsApp Business API
        
        Args:
            to_phone: Número de teléfono del destinatario
            message: Mensaje a enviar
            
        Returns:
            Dict con resultado del envío
        """
        if not self.is_enabled():
            logger.warning("Meta WhatsApp no está habilitado o configurado")
            return {'success': False, 'error': 'Meta WhatsApp no configurado'}
        
        try:
            # Formatear número de teléfono
            formatted_phone = self.format_phone_number(to_phone)
            
            # URL del endpoint de mensajes
            url = f"{self.api_base_url}/{self.phone_number_id}/messages"
            
            # Headers
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Body del mensaje
            payload = {
                'messaging_product': 'whatsapp',
                'to': formatted_phone,
                'type': 'text',
                'text': {
                    'body': message
                }
            }
            
            # Enviar mensaje
            response = requests.post(url, headers=headers, json=payload)
            
            # Verificar respuesta
            if response.status_code == 200:
                response_data = response.json()
                message_id = response_data.get('messages', [{}])[0].get('id', '')
                
                logger.info(f"Mensaje de Meta WhatsApp enviado exitosamente a {formatted_phone} (ID: {message_id})")
                return {
                    'success': True,
                    'message_id': message_id,
                    'response': response_data
                }
            else:
                error_msg = f"Error de Meta API: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'status_code': response.status_code,
                    'response': response.text
                }
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Error de conexión con Meta API: {str(e)}"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}
        except Exception as e:
            error_msg = f"Error enviando mensaje: {str(e)}"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}
    
    def send_template_message(self, to_phone: str, template_name: str, 
                            language_code: str = 'es', 
                            components: List[Dict] = None) -> Dict[str, Any]:
        """
        Envía un mensaje usando una plantilla de Meta
        
        Args:
            to_phone: Número de teléfono del destinatario
            template_name: Nombre de la plantilla aprobada en Meta
            language_code: Código de idioma (default: 'es')
            components: Lista de componentes con variables para la plantilla
            
        Returns:
            Dict con resultado del envío
        """
        if not self.is_enabled():
            logger.warning("Meta WhatsApp no está habilitado o configurado")
            return {'success': False, 'error': 'Meta WhatsApp no configurado'}
        
        try:
            # Formatear número de teléfono
            formatted_phone = self.format_phone_number(to_phone)
            
            # URL del endpoint de mensajes
            url = f"{self.api_base_url}/{self.phone_number_id}/messages"
            
            # Headers
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Body del mensaje con template
            payload = {
                'messaging_product': 'whatsapp',
                'to': formatted_phone,
                'type': 'template',
                'template': {
                    'name': template_name,
                    'language': {
                        'code': language_code
                    }
                }
            }
            
            # Agregar componentes si se proporcionan
            if components:
                payload['template']['components'] = components
            
            # Enviar mensaje
            response = requests.post(url, headers=headers, json=payload)
            
            # Verificar respuesta
            if response.status_code == 200:
                response_data = response.json()
                message_id = response_data.get('messages', [{}])[0].get('id', '')
                
                logger.info(f"Template de Meta WhatsApp enviado exitosamente a {formatted_phone} (ID: {message_id})")
                return {
                    'success': True,
                    'message_id': message_id,
                    'response': response_data
                }
            else:
                error_msg = f"Error de Meta API enviando template: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'status_code': response.status_code,
                    'response': response.text
                }
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Error de conexión con Meta API: {str(e)}"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}
        except Exception as e:
            error_msg = f"Error enviando template: {str(e)}"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}
    
    def get_message_status(self, message_id: str) -> Dict[str, Any]:
        """
        Obtiene el estado de un mensaje enviado
        
        Args:
            message_id: ID del mensaje (WAMID)
            
        Returns:
            Dict con el estado del mensaje
        """
        if not self.is_enabled():
            return {'success': False, 'error': 'Meta WhatsApp no configurado'}
        
        try:
            # URL del endpoint de estado
            url = f"{self.api_base_url}/{message_id}"
            
            # Headers
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            # Obtener estado
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f"Error obteniendo estado: {response.status_code} - {response.text}"
                }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # =========================================================================
    # Métodos específicos para el negocio de reservas
    # =========================================================================
    
    def send_reserva_confirmada(self, reserva) -> Dict[str, Any]:
        """
        Envía notificación de reserva confirmada con mensaje personalizado
        """
        if not reserva.cliente.telefono:
            logger.warning(f"Cliente {reserva.cliente.username} no tiene teléfono configurado")
            return {'success': False, 'error': 'Cliente sin teléfono'}
        
        # Preparar datos para el mensaje personalizado
        fecha_formateada = reserva.fecha.strftime('%d/%m/%Y')
        hora_formateada = reserva.hora_inicio.strftime('%H:%M')
        negocio = reserva.peluquero
        negocio_nombre = negocio.nombre
        servicio_nombre = reserva.servicio.servicio.nombre if reserva.servicio else "Servicio general"
        cliente_nombre = reserva.cliente.get_full_name() or reserva.cliente.username
        profesional_nombre = reserva.profesional.nombre_completo if reserva.profesional else negocio_nombre
        
        # Obtener dirección del negocio
        direccion = getattr(negocio, 'direccion', None) or 'Dirección no disponible'
        
        # Crear mensaje personalizado y ameno
        mensaje = f"""✅ *Confirmación de Reserva*

Hola {cliente_nombre},

Tu reserva ha sido confirmada:

📍 *Negocio:* {negocio_nombre}
👤 *Profesional:* {profesional_nombre}
✂️ *Servicio:* {servicio_nombre}
📅 *Fecha:* {fecha_formateada}
🕐 *Hora:* {hora_formateada}

🏠 *Dirección:* {direccion}

¡Te esperamos!

_Equipo Melissa_"""
        
        return self.send_text_message(reserva.cliente.telefono, mensaje)
    
    def send_recordatorio_dia_antes(self, reserva) -> Dict[str, Any]:
        """
        Envía recordatorio 1 día antes de la cita
        """
        if not reserva.cliente.telefono:
            return {'success': False, 'error': 'Cliente sin teléfono'}
        
        fecha_formateada = reserva.fecha.strftime('%d de %B de %Y')
        hora_formateada = reserva.hora_inicio.strftime('%H:%M')
        negocio_nombre = reserva.peluquero.nombre
        cliente_nombre = reserva.cliente.get_full_name() or reserva.cliente.username
        servicio_nombre = reserva.servicio.servicio.nombre if reserva.servicio else "Servicio general"
        
        # Obtener información del negocio
        direccion = getattr(reserva.peluquero, 'direccion', 'Dirección no disponible')
        telefono_negocio = getattr(reserva.peluquero, 'telefono', 'Teléfono no disponible')
        
        # URL para editar la reserva
        from django.conf import settings
        base_url = getattr(settings, 'BASE_URL', 'http://127.0.0.1:8000')
        editar_url = f"{base_url}/clientes/editar-reserva/{reserva.id}/"
        
        mensaje = f"""⏰ ¡Recordatorio! 

Hola {cliente_nombre}, mañana tienes tu cita 💄

📅 *Fecha:* {fecha_formateada}
🕐 *Hora:* {hora_formateada}
💇‍♀️ *Profesional:* {negocio_nombre}
💄 *Servicio:* {servicio_nombre}

📍 *Dirección:* {direccion}
📞 *Teléfono:* {telefono_negocio}

¡No olvides llegar puntual! Te esperamos con muchas ganas ✨

🔗 *¿Necesitas hacer cambios?*
{editar_url}

_Equipo Melissa_"""
        
        return self.send_text_message(reserva.cliente.telefono, mensaje)
    
    def send_recordatorio_tres_horas(self, reserva) -> Dict[str, Any]:
        """
        Envía recordatorio 3 horas antes de la cita
        """
        if not reserva.cliente.telefono:
            return {'success': False, 'error': 'Cliente sin teléfono'}
        
        fecha_formateada = reserva.fecha.strftime('%d de %B de %Y')
        hora_formateada = reserva.hora_inicio.strftime('%H:%M')
        negocio_nombre = reserva.peluquero.nombre
        cliente_nombre = reserva.cliente.get_full_name() or reserva.cliente.username
        servicio_nombre = reserva.servicio.servicio.nombre if reserva.servicio else "Servicio general"
        
        # Obtener información del negocio
        direccion = getattr(reserva.peluquero, 'direccion', 'Dirección no disponible')
        telefono_negocio = getattr(reserva.peluquero, 'telefono', 'Teléfono no disponible')
        
        # URL para editar la reserva
        from django.conf import settings
        from django.utils import timezone
        base_url = getattr(settings, 'BASE_URL', 'http://127.0.0.1:8000')
        editar_url = f"{base_url}/clientes/editar-reserva/{reserva.id}/"
        
        # Verificar si se puede cancelar (más de 1 hora antes)
        ahora = timezone.now()
        hora_cita = timezone.datetime.combine(reserva.fecha, reserva.hora_inicio)
        tiempo_restante = hora_cita - ahora
        puede_cancelar = tiempo_restante.total_seconds() > 3600  # Más de 1 hora
        
        mensaje = f"""⏰ ¡Último recordatorio! 

Hola {cliente_nombre}, en 3 horas tienes tu cita 💄

📅 *Fecha:* {fecha_formateada}
🕐 *Hora:* {hora_formateada}
💇‍♀️ *Profesional:* {negocio_nombre}
💄 *Servicio:* {servicio_nombre}

📍 *Dirección:* {direccion}
📞 *Teléfono:* {telefono_negocio}

¡Prepárate para verte hermosa! Te esperamos pronto ✨

🔗 *¿Necesitas hacer cambios?*
{editar_url}

{f"⚠️ *Nota:* Solo puedes cancelar con más de 1 hora de anticipación" if puede_cancelar else "❌ *No se puede cancelar* - Menos de 1 hora para la cita"}

_Equipo Melissa_"""
        
        return self.send_text_message(reserva.cliente.telefono, mensaje)
    
    def send_reserva_cancelada(self, reserva, motivo: str = "") -> Dict[str, Any]:
        """
        Envía notificación de reserva cancelada
        """
        if not reserva.cliente.telefono:
            return {'success': False, 'error': 'Cliente sin teléfono'}
        
        fecha_formateada = reserva.fecha.strftime('%d de %B de %Y')
        hora_formateada = reserva.hora_inicio.strftime('%H:%M')
        negocio_nombre = reserva.peluquero.nombre
        cliente_nombre = reserva.cliente.get_full_name() or reserva.cliente.username
        motivo_texto = motivo if motivo else "Sin motivo especificado"
        
        mensaje = f"""😔 Hola {cliente_nombre}

Tu cita ha sido cancelada:

📅 *Fecha:* {fecha_formateada}
🕐 *Hora:* {hora_formateada}
💇‍♀️ *Profesional:* {negocio_nombre}

*Motivo:* {motivo_texto}

Si necesitas reagendar tu cita, no dudes en contactarnos. ¡Estaremos encantados de atenderte! 💖

_Equipo Melissa_"""
        
        return self.send_text_message(reserva.cliente.telefono, mensaje)
    
    def send_reserva_reagendada(self, reserva, fecha_anterior, hora_anterior) -> Dict[str, Any]:
        """
        Envía notificación de reserva reagendada
        """
        if not reserva.cliente.telefono:
            return {'success': False, 'error': 'Cliente sin teléfono'}
        
        fecha_anterior_formateada = fecha_anterior.strftime('%d de %B de %Y')
        hora_anterior_formateada = hora_anterior.strftime('%H:%M')
        fecha_nueva_formateada = reserva.fecha.strftime('%d de %B de %Y')
        hora_nueva_formateada = reserva.hora_inicio.strftime('%H:%M')
        negocio_nombre = reserva.peluquero.nombre
        cliente_nombre = reserva.cliente.get_full_name() or reserva.cliente.username
        
        mensaje = f"""📅 ¡Cita reagendada! 

Hola {cliente_nombre}, tu cita ha sido reagendada:

❌ *Fecha anterior:* {fecha_anterior_formateada} a las {hora_anterior_formateada}
✅ *Nueva fecha:* {fecha_nueva_formateada} a las {hora_nueva_formateada}
💇‍♀️ *Profesional:* {negocio_nombre}

¡Te esperamos en tu nueva fecha! Si necesitas hacer algún otro cambio, no dudes en contactarnos ✨

_Equipo Melissa_"""
        
        return self.send_text_message(reserva.cliente.telefono, mensaje)
    
    def send_inasistencia(self, reserva, motivo: str = "") -> Dict[str, Any]:
        """
        Envía notificación de inasistencia
        """
        if not reserva.cliente.telefono:
            return {'success': False, 'error': 'Cliente sin teléfono'}
        
        fecha_formateada = reserva.fecha.strftime('%d de %B de %Y')
        hora_formateada = reserva.hora_inicio.strftime('%H:%M')
        negocio_nombre = reserva.peluquero.nombre
        cliente_nombre = reserva.cliente.get_full_name() or reserva.cliente.username
        motivo_texto = motivo if motivo else "Sin motivo especificado"
        
        mensaje = f"""😔 Hola {cliente_nombre}

Notamos que no pudiste asistir a tu cita:

📅 *Fecha:* {fecha_formateada}
🕐 *Hora:* {hora_formateada}
💇‍♀️ *Profesional:* {negocio_nombre}

*Motivo registrado:* {motivo_texto}

Entendemos que pueden surgir imprevistos. Si quieres reagendar tu cita, estaremos encantados de atenderte en otro momento 💖

_Equipo Melissa_"""
        
        return self.send_text_message(reserva.cliente.telefono, mensaje)


# Instancia global del servicio
meta_whatsapp_service = MetaWhatsAppService()


