import requests
import json
import logging
from django.conf import settings
from django.utils import timezone
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class WhatsAppService:
    """
    Servicio para manejar notificaciones por WhatsApp Business API
    """
    
    def __init__(self):
        self.config = settings.WHATSAPP_CONFIG
        # Configuración compatible con Twilio
        self.api_url = self.config.get('API_URL', 'https://api.twilio.com')
        self.phone_number_id = self.config.get('PHONE_NUMBER_ID', self.config.get('WHATSAPP_NUMBER', ''))
        self.access_token = self.config.get('ACCESS_TOKEN', self.config.get('AUTH_TOKEN', ''))
        self.verify_token = self.config.get('VERIFY_TOKEN', '')
        
    def is_enabled(self):
        """Verifica si WhatsApp está habilitado y configurado"""
        return (
            self.config.get('ENABLED', False) and 
            self.phone_number_id and 
            self.access_token
        )
    
    def format_phone_number(self, phone_number):
        """
        Formatea el número de teléfono para WhatsApp
        Elimina espacios, guiones y agrega código de país si es necesario
        """
        # Limpiar el número
        cleaned = re.sub(r'[\s\-\(\)]', '', phone_number)
        
        # Si no tiene código de país, agregar +57 (Colombia)
        if not cleaned.startswith('+'):
            if cleaned.startswith('57'):
                cleaned = '+' + cleaned
            elif cleaned.startswith('0'):
                cleaned = '+57' + cleaned[1:]
            else:
                cleaned = '+57' + cleaned
        
        return cleaned
    
    def send_template_message(self, to_phone, template_name, language_code='es', components=None):
        """
        Envía un mensaje usando una plantilla predefinida
        """
        if not self.is_enabled():
            logger.warning("WhatsApp no está habilitado o configurado")
            return False
        
        try:
            url = f"{self.api_url}/{self.phone_number_id}/messages"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'messaging_product': 'whatsapp',
                'to': self.format_phone_number(to_phone),
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
                data['template']['components'] = components
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                logger.info(f"Mensaje de WhatsApp enviado exitosamente a {to_phone}")
                return True
            else:
                logger.error(f"Error enviando mensaje de WhatsApp: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error en WhatsAppService.send_template_message: {str(e)}")
            return False
    
    def send_custom_message(self, to_phone, message):
        """
        Envía un mensaje personalizado (texto simple)
        """
        if not self.is_enabled():
            logger.warning("WhatsApp no está habilitado o configurado")
            return False
        
        try:
            url = f"{self.api_url}/{self.phone_number_id}/messages"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'messaging_product': 'whatsapp',
                'to': self.format_phone_number(to_phone),
                'type': 'text',
                'text': {
                    'body': message
                }
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                logger.info(f"Mensaje personalizado de WhatsApp enviado a {to_phone}")
                return True
            else:
                logger.error(f"Error enviando mensaje personalizado: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error en WhatsAppService.send_custom_message: {str(e)}")
            return False
    
    def send_reserva_confirmada(self, reserva):
        """
        Envía notificación de reserva confirmada
        """
        if not reserva.cliente.telefono:
            logger.warning(f"Cliente {reserva.cliente.username} no tiene teléfono configurado")
            return False
        
        template_name = self.config['TEMPLATES']['reserva_confirmada']
        
        # Preparar variables para la plantilla
        fecha_formateada = reserva.fecha.strftime('%d/%m/%Y')
        hora_formateada = reserva.hora_inicio.strftime('%H:%M')
        negocio_nombre = reserva.peluquero.nombre
        servicio_nombre = reserva.servicio.servicio.nombre if reserva.servicio else "Servicio general"
        
        components = [
            {
                "type": "body",
                "parameters": [
                    {"type": "text", "text": reserva.cliente.get_full_name() or reserva.cliente.username},
                    {"type": "text", "text": negocio_nombre},
                    {"type": "text", "text": servicio_nombre},
                    {"type": "text", "text": fecha_formateada},
                    {"type": "text", "text": hora_formateada}
                ]
            }
        ]
        
        return self.send_template_message(
            reserva.cliente.telefono,
            template_name,
            components=components
        )
    
    def send_recordatorio_dia_antes(self, reserva):
        """
        Envía recordatorio 1 día antes de la cita
        """
        if not reserva.cliente.telefono:
            return False
        
        template_name = self.config['TEMPLATES']['recordatorio_dia_antes']
        
        fecha_formateada = reserva.fecha.strftime('%d/%m/%Y')
        hora_formateada = reserva.hora_inicio.strftime('%H:%M')
        negocio_nombre = reserva.peluquero.nombre
        
        components = [
            {
                "type": "body",
                "parameters": [
                    {"type": "text", "text": reserva.cliente.get_full_name() or reserva.cliente.username},
                    {"type": "text", "text": negocio_nombre},
                    {"type": "text", "text": fecha_formateada},
                    {"type": "text", "text": hora_formateada}
                ]
            }
        ]
        
        return self.send_template_message(
            reserva.cliente.telefono,
            template_name,
            components=components
        )
    
    def send_recordatorio_tres_horas(self, reserva):
        """
        Envía recordatorio 3 horas antes de la cita
        """
        if not reserva.cliente.telefono:
            return False
        
        template_name = self.config['TEMPLATES']['recordatorio_tres_horas']
        
        fecha_formateada = reserva.fecha.strftime('%d/%m/%Y')
        hora_formateada = reserva.hora_inicio.strftime('%H:%M')
        negocio_nombre = reserva.peluquero.nombre
        
        components = [
            {
                "type": "body",
                "parameters": [
                    {"type": "text", "text": reserva.cliente.get_full_name() or reserva.cliente.username},
                    {"type": "text", "text": negocio_nombre},
                    {"type": "text", "text": fecha_formateada},
                    {"type": "text", "text": hora_formateada}
                ]
            }
        ]
        
        return self.send_template_message(
            reserva.cliente.telefono,
            template_name,
            components=components
        )
    
    def send_reserva_cancelada(self, reserva, motivo=""):
        """
        Envía notificación de reserva cancelada
        """
        if not reserva.cliente.telefono:
            return False
        
        template_name = self.config['TEMPLATES']['reserva_cancelada']
        
        fecha_formateada = reserva.fecha.strftime('%d/%m/%Y')
        hora_formateada = reserva.hora_inicio.strftime('%H:%M')
        negocio_nombre = reserva.peluquero.nombre
        motivo_texto = motivo if motivo else "Sin motivo especificado"
        
        components = [
            {
                "type": "body",
                "parameters": [
                    {"type": "text", "text": reserva.cliente.get_full_name() or reserva.cliente.username},
                    {"type": "text", "text": negocio_nombre},
                    {"type": "text", "text": fecha_formateada},
                    {"type": "text", "text": hora_formateada},
                    {"type": "text", "text": motivo_texto}
                ]
            }
        ]
        
        return self.send_template_message(
            reserva.cliente.telefono,
            template_name,
            components=components
        )
    
    def send_reserva_reagendada(self, reserva, fecha_anterior, hora_anterior):
        """
        Envía notificación de reserva reagendada
        """
        if not reserva.cliente.telefono:
            return False
        
        template_name = self.config['TEMPLATES']['reserva_reagendada']
        
        fecha_anterior_formateada = fecha_anterior.strftime('%d/%m/%Y')
        hora_anterior_formateada = hora_anterior.strftime('%H:%M')
        fecha_nueva_formateada = reserva.fecha.strftime('%d/%m/%Y')
        hora_nueva_formateada = reserva.hora_inicio.strftime('%H:%M')
        negocio_nombre = reserva.peluquero.nombre
        
        components = [
            {
                "type": "body",
                "parameters": [
                    {"type": "text", "text": reserva.cliente.get_full_name() or reserva.cliente.username},
                    {"type": "text", "text": negocio_nombre},
                    {"type": "text", "text": fecha_anterior_formateada},
                    {"type": "text", "text": hora_anterior_formateada},
                    {"type": "text", "text": fecha_nueva_formateada},
                    {"type": "text", "text": hora_nueva_formateada}
                ]
            }
        ]
        
        return self.send_template_message(
            reserva.cliente.telefono,
            template_name,
            components=components
        )
    
    def send_inasistencia(self, reserva, motivo=""):
        """
        Envía notificación de inasistencia
        """
        if not reserva.cliente.telefono:
            return False
        
        template_name = self.config['TEMPLATES']['inasistencia']
        
        fecha_formateada = reserva.fecha.strftime('%d/%m/%Y')
        hora_formateada = reserva.hora_inicio.strftime('%H:%M')
        negocio_nombre = reserva.peluquero.nombre
        motivo_texto = motivo if motivo else "Sin motivo especificado"
        
        components = [
            {
                "type": "body",
                "parameters": [
                    {"type": "text", "text": reserva.cliente.get_full_name() or reserva.cliente.username},
                    {"type": "text", "text": negocio_nombre},
                    {"type": "text", "text": fecha_formateada},
                    {"type": "text", "text": hora_formateada},
                    {"type": "text", "text": motivo_texto}
                ]
            }
        ]
        
        return self.send_template_message(
            reserva.cliente.telefono,
            template_name,
            components=components
        )

# Instancia global del servicio
whatsapp_service = WhatsAppService() 