"""
Servicio de WhatsApp usando Twilio
Reemplaza completamente la API de Meta
"""

import logging
from typing import Dict, List, Optional, Any
from django.conf import settings
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
import re

logger = logging.getLogger(__name__)

class TwilioWhatsAppService:
    """
    Servicio principal para WhatsApp usando Twilio
    Maneja mensajes, templates y notificaciones
    """
    
    def __init__(self):
        self.config = settings.WHATSAPP_CONFIG
        self.account_sid = self.config['ACCOUNT_SID']
        self.auth_token = self.config['AUTH_TOKEN']
        self.whatsapp_number = self.config['WHATSAPP_NUMBER']
        self.enabled = self.config['ENABLED']
        
        # Inicializar cliente de Twilio
        try:
            self.client = Client(self.account_sid, self.auth_token)
            logger.info("Cliente de Twilio WhatsApp inicializado correctamente")
        except Exception as e:
            logger.error(f"Error inicializando cliente de Twilio: {e}")
            self.client = None
        
    def is_enabled(self) -> bool:
        """Verifica si WhatsApp está habilitado y configurado correctamente"""
        return self.enabled and self.client is not None
    
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

    def _prepare_template_variable(self, text: str, max_len: int = 900) -> str:
        """
        WhatsApp templates (Content API) pueden ser más estrictos con algunos caracteres/formato.
        Normalizamos para minimizar rechazos y limitamos el tamaño del parámetro.
        """
        if text is None:
            return ""
        s = str(text)
        # Normalizar saltos de línea
        s = s.replace("\r\n", "\n").replace("\r", "\n")
        # Evitar caracteres de formato que a veces generan problemas como parámetro template
        s = s.replace("\u200e", "").replace("\u200f", "")  # LRM/RLM
        # Reducir exceso de espacios
        s = re.sub(r"[ \t]+", " ", s)
        # Limitar longitud (dejamos margen)
        if len(s) > max_len:
            s = s[: max_len - 1] + "…"
        return s.strip()

    def _get_template_sid(self, template_key: str) -> str:
        templates = (self.config.get("TEMPLATES") or {})
        return (templates.get(template_key) or "").strip()

    def _send_event_template(self, template_key: str, to_phone: str, variables: Dict[str, str]) -> Dict[str, Any]:
        """
        Envía un template específico por evento si está configurado.
        Si no existe, cae a send_text_message (que a su vez intentará texto_libre si existe).
        """
        sid = self._get_template_sid(template_key)
        if sid:
            logger.info(f"Enviando WhatsApp con template '{template_key}' (Content SID configurado)")
            return self.send_template_message(to_phone=to_phone, template_name=sid, variables=variables)
        logger.warning(
            f"No hay Content SID configurado para template '{template_key}'. "
            f"Configura WHATSAPP_CONFIG['TEMPLATES']['{template_key}'] (por env) para producción."
        )
        # Fallback: texto libre (si texto_libre existe) o body directo (probablemente 63016 fuera de ventana).
        joined = " | ".join([self._prepare_template_variable(v, max_len=200) for v in variables.values() if v is not None])
        return self.send_text_message(to_phone=to_phone, message=joined)
    
    def send_text_message(self, to_phone: str, message: str) -> Dict[str, Any]:
        """
        Envía un mensaje de texto simple
        
        Args:
            to_phone: Número de teléfono del destinatario
            message: Mensaje a enviar
            
        Returns:
            Dict con resultado del envío
        """
        if not self.is_enabled():
            logger.warning("WhatsApp no está habilitado o configurado")
            return {'success': False, 'error': 'WhatsApp no configurado'}
        
        try:
            # Si existe una plantilla genérica (texto_libre), enviamos SIEMPRE como template.
            # Esto evita "undelivered 63016" (WhatsApp exige template fuera de ventana / primer contacto).
            templates = self.config.get("TEMPLATES") or {}
            texto_libre_sid = templates.get("texto_libre")
            if texto_libre_sid:
                var_key = str(self.config.get("TEXTO_LIBRE_VAR_KEY") or "1").strip()
                logger.info("Enviando WhatsApp como template texto_libre (Content SID)")
                return self.send_template_message(
                    to_phone=to_phone,
                    template_name=texto_libre_sid,
                    variables={var_key: self._prepare_template_variable(message)},
                )

            # Formatear número de teléfono
            formatted_phone = self.format_phone_number(to_phone)
            wa_from = self.whatsapp_number.lstrip('whatsapp:').strip()
            if not wa_from.startswith('+'):
                wa_from = '+' + wa_from

            # Enviar mensaje de WhatsApp
            message_obj = self.client.messages.create(
                from_=f'whatsapp:{wa_from}',
                body=message,
                to=f'whatsapp:{formatted_phone}'
            )
            
            logger.info(f"Mensaje de WhatsApp enviado exitosamente a {formatted_phone}")
            return {
                'success': True,
                'message_id': message_obj.sid,
                'response': {
                    'sid': message_obj.sid,
                    'status': message_obj.status,
                    'to': formatted_phone
                }
            }
            
        except TwilioException as e:
            error_code = getattr(e, 'code', None)
            # 63112: Meta/WhatsApp deshabilitó la cuenta/sender (no es un problema de código).
            if str(error_code) == "63112":
                logger.error(
                    "Twilio 63112: Sender/WABA deshabilitado por Meta. "
                    "Debes reactivar el WhatsApp Sender en Twilio/Meta para poder enviar."
                )
                # Evitar ruido: marcar como deshabilitado en runtime hasta reinicio.
                self.enabled = False
                return {
                    'success': False,
                    'error_code': error_code,
                    'error': 'WhatsApp deshabilitado por Meta (Twilio 63112).',
                }

            error_msg = f"Error de Twilio enviando mensaje: {str(e)}"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg, 'error_code': error_code}
        except Exception as e:
            error_msg = f"Error enviando mensaje: {str(e)}"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}
    
    def send_template_message(self, to_phone: str, template_name: str, 
                            variables: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Envía un mensaje usando una plantilla de Twilio
        
        Args:
            to_phone: Número de teléfono del destinatario
            template_name: Nombre de la plantilla (Content SID)
            variables: Variables para la plantilla
            
        Returns:
            Dict con resultado del envío
        """
        if not self.is_enabled():
            logger.warning("WhatsApp no está habilitado o configurado")
            return {'success': False, 'error': 'WhatsApp no configurado'}
        
        try:
            # Formatear número de teléfono
            formatted_phone = self.format_phone_number(to_phone)
            # Asegurar que whatsapp_number no tenga ya el prefijo
            wa_from = self.whatsapp_number.lstrip('whatsapp:').strip()
            if not wa_from.startswith('+'):
                wa_from = '+' + wa_from

            # Preparar variables para la plantilla
            content_variables = '{}'
            if variables:
                import json
                safe_vars = {str(k): self._prepare_template_variable(v) for k, v in variables.items()}
                content_variables = json.dumps(safe_vars)
            
            # Enviar mensaje de plantilla
            message_obj = self.client.messages.create(
                from_=f'whatsapp:{wa_from}',
                content_sid=template_name,
                content_variables=content_variables,
                to=f'whatsapp:{formatted_phone}'
            )
            
            logger.warning(f"Template WhatsApp enviado a {formatted_phone} — SID: {message_obj.sid} — status: {message_obj.status}")
            return {
                'success': True,
                'message_id': message_obj.sid,
                'response': {
                    'sid': message_obj.sid,
                    'status': message_obj.status,
                    'to': formatted_phone
                }
            }
            
        except TwilioException as e:
            error_code = getattr(e, 'code', None)
            if str(error_code) == "63112":
                logger.error(
                    "Twilio 63112: Sender/WABA deshabilitado por Meta. "
                    "Debes reactivar el WhatsApp Sender en Twilio/Meta para poder enviar."
                )
                self.enabled = False
                return {
                    'success': False,
                    'error_code': error_code,
                    'error': 'WhatsApp deshabilitado por Meta (Twilio 63112).',
                }

            # 21656: Content Variables inválidas (normalmente clave de variable no coincide con el template)
            if str(error_code) == "21656" and variables:
                try:
                    templates = self.config.get("TEMPLATES") or {}
                    texto_libre_sid = templates.get("texto_libre")
                    if texto_libre_sid and template_name == texto_libre_sid:
                        # Reintentar con claves comunes: "1" y "body"
                        msg = next(iter(variables.values()))
                        for alt_key in ("1", "body"):
                            if alt_key in variables:
                                continue
                            logger.warning(f"Twilio 21656: reintentando texto_libre con variable '{alt_key}'")
                            return self.send_template_message(
                                to_phone=to_phone,
                                template_name=template_name,
                                variables={alt_key: msg},
                            )
                except Exception as retry_err:
                    logger.warning(f"No se pudo reintentar tras 21656: {retry_err}")

            error_msg = f"Error de Twilio enviando template: {str(e)}"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg, 'error_code': error_code}
        except Exception as e:
            error_msg = f"Error enviando template: {str(e)}"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}
    
    def get_message_status(self, message_id: str) -> Dict[str, Any]:
        """
        Obtiene el estado de un mensaje enviado
        
        Args:
            message_id: ID del mensaje (SID)
            
        Returns:
            Dict con el estado del mensaje
        """
        try:
            message = self.client.messages(message_id).fetch()
            # Si el sender/WABA está deshabilitado por Meta, lo marcamos para evitar ruido.
            # Nota: a veces Twilio devuelve 63112 solo al consultar el status (no en el create()).
            if str(getattr(message, "error_code", None)) == "63112":
                logger.error(
                    "Twilio 63112 detectado en status: Sender/WABA deshabilitado por Meta. "
                    "No se podrán enviar mensajes hasta reactivar el WhatsApp Sender."
                )
                self.enabled = False
            if str(getattr(message, "error_code", None)) == "63016":
                logger.warning(
                    "Twilio 63016 detectado en status: el mensaje no fue aceptado por reglas de plantilla/ventana. "
                    "En producción esto suele indicar template no aprobado/incorrecto (Utility/Business initiated) "
                    "o conversación fuera de ventana 24h."
                )
            return {
                'success': True,
                'data': {
                    'sid': message.sid,
                    'status': message.status,
                    'to': message.to,
                    'from': message.from_,
                    'body': message.body,
                    'error_code': message.error_code,
                    'error_message': message.error_message,
                    'num_segments': getattr(message, 'num_segments', None),
                    'price': getattr(message, 'price', None),
                    'price_unit': getattr(message, 'price_unit', None),
                    'date_created': message.date_created.isoformat() if message.date_created else None,
                    'date_sent': message.date_sent.isoformat() if message.date_sent else None,
                    'date_updated': message.date_updated.isoformat() if message.date_updated else None,
                }
            }
        except TwilioException as e:
            return {'success': False, 'error': f"Error obteniendo estado: {str(e)}"}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # Métodos específicos para el negocio de reservas
    
    def _get_telefono(self, reserva) -> str:
        """Obtiene el teléfono del cliente (con cuenta o provisional)."""
        return reserva.get_cliente_telefono() if hasattr(reserva, 'get_cliente_telefono') else (
            (reserva.cliente.telefono if reserva.cliente else '') or
            (reserva.cliente_provisional.telefono if reserva.cliente_provisional else '')
        )

    def _get_nombre(self, reserva) -> str:
        """Obtiene el nombre del cliente (con cuenta o provisional)."""
        if hasattr(reserva, 'get_cliente_nombre'):
            return reserva.get_cliente_nombre()
        if reserva.cliente:
            return reserva.cliente.get_full_name() or reserva.cliente.username
        if reserva.cliente_provisional:
            return reserva.cliente_provisional.nombre
        return 'Cliente'

    def send_reserva_confirmada(self, reserva) -> Dict[str, Any]:
        """
        Envía notificación de reserva confirmada con mensaje personalizado
        """
        telefono = self._get_telefono(reserva)
        if not telefono:
            cliente_id = getattr(reserva.cliente, 'username', None) or getattr(reserva.cliente_provisional, 'nombre', 'provisional')
            logger.warning(f"Reserva {reserva.id}: cliente '{cliente_id}' no tiene teléfono — notificación omitida")
            return {'success': False, 'error': 'Cliente sin teléfono'}

        fecha_formateada = reserva.fecha.strftime('%d/%m/%Y')
        hora_formateada = reserva.hora_inicio.strftime('%H:%M')
        negocio = reserva.peluquero
        negocio_nombre = negocio.nombre
        servicio_nombre = reserva.servicio.servicio.nombre if reserva.servicio else "Servicio general"
        cliente_nombre = self._get_nombre(reserva)
        profesional_nombre = reserva.profesional.nombre_completo if reserva.profesional else negocio_nombre
        direccion = getattr(negocio, 'direccion', None) or 'Dirección no disponible'

        return self._send_event_template(
            template_key="reserva_confirmada",
            to_phone=telefono,
            variables={
                "1": cliente_nombre,
                "2": negocio_nombre,
                "3": servicio_nombre,
                "4": fecha_formateada,
                "5": hora_formateada,
                "6": profesional_nombre,
                "7": direccion,
            },
        )
    
    def send_recordatorio_dia_antes(self, reserva) -> Dict[str, Any]:
        """
        Envía recordatorio 1 día antes de la cita con información completa y botones
        """
        telefono = self._get_telefono(reserva)
        if not telefono:
            logger.warning(f"Reserva {reserva.id}: sin teléfono para recordatorio día antes")
            return {'success': False, 'error': 'Cliente sin teléfono'}
        
        fecha_formateada = reserva.fecha.strftime('%d de %B de %Y')
        hora_formateada = reserva.hora_inicio.strftime('%H:%M')
        negocio_nombre = reserva.peluquero.nombre
        cliente_nombre = self._get_nombre(reserva)
        servicio_nombre = reserva.servicio.servicio.nombre if reserva.servicio else "Servicio general"

        direccion = getattr(reserva.peluquero, 'direccion', 'Dirección no disponible')
        telefono_negocio = getattr(reserva.peluquero, 'telefono', 'Teléfono no disponible')

        from django.conf import settings
        base_url = getattr(settings, 'BASE_URL', 'https://appo.com.co')
        editar_url = f"{base_url}/clientes/editar-reserva/{reserva.id}/"

        return self._send_event_template(
            template_key="recordatorio_dia_antes",
            to_phone=telefono,
            variables={
                "1": cliente_nombre,
                "2": negocio_nombre,
                "3": servicio_nombre,
                "4": fecha_formateada,
                "5": hora_formateada,
                "6": direccion,
                "7": telefono_negocio,
                "8": editar_url,
            },
        )
    
    def send_recordatorio_tres_horas(self, reserva) -> Dict[str, Any]:
        """
        Envía recordatorio 3 horas antes de la cita con información y botones
        """
        telefono = self._get_telefono(reserva)
        if not telefono:
            logger.warning(f"Reserva {reserva.id}: sin teléfono para recordatorio 3 horas")
            return {'success': False, 'error': 'Cliente sin teléfono'}

        fecha_formateada = reserva.fecha.strftime('%d de %B de %Y')
        hora_formateada = reserva.hora_inicio.strftime('%H:%M')
        negocio_nombre = reserva.peluquero.nombre
        cliente_nombre = self._get_nombre(reserva)
        servicio_nombre = reserva.servicio.servicio.nombre if reserva.servicio else "Servicio general"

        direccion = getattr(reserva.peluquero, 'direccion', 'Dirección no disponible')
        telefono_negocio = getattr(reserva.peluquero, 'telefono', 'Teléfono no disponible')

        from django.conf import settings
        base_url = getattr(settings, 'BASE_URL', 'https://appo.com.co')
        editar_url = f"{base_url}/clientes/editar-reserva/{reserva.id}/"
        
        # Verificar si se puede cancelar (más de 1 hora antes)
        from django.utils import timezone
        from datetime import datetime
        ahora = timezone.now()
        hora_cita = datetime.combine(reserva.fecha, reserva.hora_inicio)
        # Asegurar compatibilidad naive/aware
        if timezone.is_aware(ahora) and timezone.is_naive(hora_cita):
            hora_cita = timezone.make_aware(hora_cita, timezone.get_current_timezone())
        tiempo_restante = hora_cita - ahora
        
        puede_cancelar = tiempo_restante.total_seconds() > 3600

        nota_cancelacion = (
            "Puedes cancelar con más de 1 hora de anticipación"
            if puede_cancelar
            else "No se puede cancelar: falta menos de 1 hora"
        )
        return self._send_event_template(
            template_key="recordatorio_tres_horas",
            to_phone=telefono,
            variables={
                "1": cliente_nombre,
                "2": negocio_nombre,
                "3": servicio_nombre,
                "4": fecha_formateada,
                "5": hora_formateada,
                "6": direccion,
                "7": telefono_negocio,
                "8": editar_url,
                "9": nota_cancelacion,
            },
        )
    
    def send_reserva_cancelada(self, reserva, motivo: str = "") -> Dict[str, Any]:
        """
        Envía notificación de reserva cancelada
        """
        telefono = self._get_telefono(reserva)
        if not telefono:
            logger.warning(f"Reserva {reserva.id}: sin teléfono para notificación de cancelación")
            return {'success': False, 'error': 'Cliente sin teléfono'}

        fecha_formateada = reserva.fecha.strftime('%d de %B de %Y')
        hora_formateada = reserva.hora_inicio.strftime('%H:%M')
        negocio_nombre = reserva.peluquero.nombre
        cliente_nombre = self._get_nombre(reserva)
        motivo_texto = motivo if motivo else "Sin motivo especificado"

        return self._send_event_template(
            template_key="reserva_cancelada",
            to_phone=telefono,
            variables={
                "1": cliente_nombre,
                "2": negocio_nombre,
                "3": fecha_formateada,
                "4": hora_formateada,
                "5": motivo_texto,
            },
        )
    
    def send_reserva_reagendada(self, reserva, fecha_anterior, hora_anterior) -> Dict[str, Any]:
        """
        Envía notificación de reserva reagendada
        """
        telefono = self._get_telefono(reserva)
        if not telefono:
            logger.warning(f"Reserva {reserva.id}: sin teléfono para notificación de reagendamiento")
            return {'success': False, 'error': 'Cliente sin teléfono'}

        fecha_anterior_formateada = fecha_anterior.strftime('%d de %B de %Y')
        hora_anterior_formateada = hora_anterior.strftime('%H:%M')
        fecha_nueva_formateada = reserva.fecha.strftime('%d de %B de %Y')
        hora_nueva_formateada = reserva.hora_inicio.strftime('%H:%M')
        negocio_nombre = reserva.peluquero.nombre
        cliente_nombre = self._get_nombre(reserva)

        return self._send_event_template(
            template_key="reserva_reagendada",
            to_phone=telefono,
            variables={
                "1": cliente_nombre,
                "2": negocio_nombre,
                "3": fecha_anterior_formateada,
                "4": hora_anterior_formateada,
                "5": fecha_nueva_formateada,
                "6": hora_nueva_formateada,
            },
        )
    
    def send_inasistencia(self, reserva, motivo: str = "") -> Dict[str, Any]:
        """
        Envía notificación de inasistencia
        """
        telefono = self._get_telefono(reserva)
        if not telefono:
            logger.warning(f"Reserva {reserva.id}: sin teléfono para notificación de inasistencia")
            return {'success': False, 'error': 'Cliente sin teléfono'}

        fecha_formateada = reserva.fecha.strftime('%d de %B de %Y')
        hora_formateada = reserva.hora_inicio.strftime('%H:%M')
        negocio_nombre = reserva.peluquero.nombre
        cliente_nombre = self._get_nombre(reserva)
        motivo_texto = motivo if motivo else "Sin motivo especificado"

        return self._send_event_template(
            template_key="inasistencia",
            to_phone=telefono,
            variables={
                "1": cliente_nombre,
                "2": negocio_nombre,
                "3": fecha_formateada,
                "4": hora_formateada,
                "5": motivo_texto,
            },
        )

# Instancia global del servicio
twilio_whatsapp_service = TwilioWhatsAppService()
