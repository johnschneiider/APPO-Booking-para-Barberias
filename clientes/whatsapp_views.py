from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.conf import settings
import json
import logging
import hmac
import hashlib
from .utils import get_whatsapp_service

logger = logging.getLogger(__name__)

@require_GET
def whatsapp_webhook_verify(request):
    """
    Endpoint para verificar el webhook de WhatsApp
    """
    try:
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        
        if mode == 'subscribe' and token == settings.WHATSAPP_CONFIG['VERIFY_TOKEN']:
            logger.info("Webhook de WhatsApp verificado exitosamente")
            return HttpResponse(challenge, content_type='text/plain')
        else:
            logger.warning("Verificación de webhook fallida")
            return HttpResponse('Forbidden', status=403)
            
    except Exception as e:
        logger.error(f"Error en verificación de webhook: {str(e)}")
        return HttpResponse('Internal Server Error', status=500)

@csrf_exempt
@require_POST
def whatsapp_webhook(request):
    """
    Endpoint para recibir mensajes de WhatsApp
    """
    try:
        # Verificar la firma del webhook (opcional pero recomendado)
        signature = request.headers.get('X-Hub-Signature-256', '')
        if not verify_webhook_signature(request.body, signature):
            logger.warning("Firma de webhook inválida")
            return HttpResponse('Unauthorized', status=401)
        
        # Parsear el payload
        payload = json.loads(request.body)
        logger.info(f"Webhook recibido: {payload}")
        
        # Procesar el mensaje
        if 'object' in payload and payload['object'] == 'whatsapp_business_account':
            for entry in payload.get('entry', []):
                for change in entry.get('changes', []):
                    if change.get('value', {}).get('messages'):
                        for message in change['value']['messages']:
                            process_whatsapp_message(message)
        
        return HttpResponse('OK', status=200)
        
    except Exception as e:
        logger.error(f"Error procesando webhook de WhatsApp: {str(e)}")
        return HttpResponse('Internal Server Error', status=500)

def verify_webhook_signature(body, signature):
    """
    Verifica la firma del webhook de WhatsApp
    """
    try:
        if not signature:
            logger.warning("Webhook recibido sin firma X-Hub-Signature-256 — rechazado")
            return False  # Rechazar si no hay firma
        
        # Extraer la firma del header
        if signature.startswith('sha256='):
            signature = signature[7:]
        
        # Calcular la firma esperada
        expected_signature = hmac.new(
            settings.META_WHATSAPP_WEBHOOK_SECRET.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
        
    except Exception as e:
        logger.error(f"Error verificando firma: {str(e)}")
        return False

def process_whatsapp_message(message):
    """
    Procesa un mensaje recibido de WhatsApp
    """
    try:
        message_type = message.get('type')
        from_number = message.get('from')
        timestamp = message.get('timestamp')
        
        logger.info(f"Procesando mensaje de WhatsApp: tipo={message_type}, from={from_number}")
        
        if message_type == 'text':
            text = message.get('text', {}).get('body', '')
            handle_text_message(from_number, text, timestamp)
        elif message_type == 'button':
            button_text = message.get('button', {}).get('text', '')
            handle_button_message(from_number, button_text, timestamp)
        elif message_type == 'interactive':
            interactive = message.get('interactive', {})
            handle_interactive_message(from_number, interactive, timestamp)
        else:
            logger.info(f"Tipo de mensaje no manejado: {message_type}")
            
    except Exception as e:
        logger.error(f"Error procesando mensaje de WhatsApp: {str(e)}")

def handle_text_message(from_number, text, timestamp):
    """
    Maneja mensajes de texto de WhatsApp
    """
    try:
        # Aquí puedes implementar la lógica para manejar diferentes comandos
        text_lower = text.lower().strip()
        
        if text_lower in ['hola', 'buenos dias', 'buenas']:
            send_welcome_message(from_number)
        elif text_lower in ['ayuda', 'help']:
            send_help_message(from_number)
        elif text_lower in ['reservas', 'mis reservas']:
            send_reservas_info(from_number)
        elif text_lower in ['cancelar', 'cancelar reserva']:
            send_cancel_instructions(from_number)
        else:
            send_default_response(from_number)
            
    except Exception as e:
        logger.error(f"Error manejando mensaje de texto: {str(e)}")

def handle_button_message(from_number, button_text, timestamp):
    """
    Maneja mensajes de botones de WhatsApp
    """
    try:
        if button_text == 'Ver Reservas':
            send_reservas_info(from_number)
        elif button_text == 'Nueva Reserva':
            send_new_reservation_info(from_number)
        elif button_text == 'Cancelar Reserva':
            send_cancel_instructions(from_number)
        elif button_text == 'Contactar':
            send_contact_info(from_number)
        else:
            send_default_response(from_number)
            
    except Exception as e:
        logger.error(f"Error manejando mensaje de botón: {str(e)}")

def handle_interactive_message(from_number, interactive, timestamp):
    """
    Maneja mensajes interactivos de WhatsApp
    """
    try:
        interactive_type = interactive.get('type')
        
        if interactive_type == 'button_reply':
            button_text = interactive.get('button_reply', {}).get('title', '')
            handle_button_message(from_number, button_text, timestamp)
        elif interactive_type == 'list_reply':
            list_reply = interactive.get('list_reply', {})
            selected_option = list_reply.get('title', '')
            handle_list_selection(from_number, selected_option, timestamp)
        else:
            send_default_response(from_number)
            
    except Exception as e:
        logger.error(f"Error manejando mensaje interactivo: {str(e)}")

def handle_list_selection(from_number, selected_option, timestamp):
    """
    Maneja selecciones de listas de WhatsApp
    """
    try:
        if selected_option == 'Ver mis reservas':
            send_reservas_info(from_number)
        elif selected_option == 'Hacer nueva reserva':
            send_new_reservation_info(from_number)
        elif selected_option == 'Cancelar reserva':
            send_cancel_instructions(from_number)
        elif selected_option == 'Contactar soporte':
            send_contact_info(from_number)
        else:
            send_default_response(from_number)
            
    except Exception as e:
        logger.error(f"Error manejando selección de lista: {str(e)}")

# Funciones de respuesta
def send_welcome_message(to_number):
    """Envía mensaje de bienvenida"""
    whatsapp_service = get_whatsapp_service()
    if not whatsapp_service or not whatsapp_service.is_enabled():
        logger.warning("WhatsApp no disponible para enviar welcome_message")
        return

    message = """¡Hola! 👋

Bienvenido a Melissa, tu sistema de reservas de belleza.

¿En qué puedo ayudarte hoy?

• Para ver tus reservas: escribe "reservas"
• Para hacer una nueva reserva: visita nuestra web
• Para cancelar: escribe "cancelar"
• Para ayuda: escribe "ayuda"

¡Estamos aquí para ayudarte! 💅✨"""
    
    if hasattr(whatsapp_service, "send_custom_message"):
        whatsapp_service.send_custom_message(to_number, message)
    else:
        whatsapp_service.send_text_message(to_number, message)

def send_help_message(to_number):
    """Envía mensaje de ayuda"""
    whatsapp_service = get_whatsapp_service()
    if not whatsapp_service or not whatsapp_service.is_enabled():
        logger.warning("WhatsApp no disponible para enviar help_message")
        return

    message = """🔧 Ayuda - Melissa

Comandos disponibles:
• "reservas" - Ver tus reservas activas
• "cancelar" - Instrucciones para cancelar
• "ayuda" - Mostrar esta ayuda

Para hacer una nueva reserva, visita nuestra página web.

¿Necesitas algo más? 😊"""
    
    if hasattr(whatsapp_service, "send_custom_message"):
        whatsapp_service.send_custom_message(to_number, message)
    else:
        whatsapp_service.send_text_message(to_number, message)

def send_reservas_info(to_number):
    """Envía información de reservas"""
    whatsapp_service = get_whatsapp_service()
    if not whatsapp_service or not whatsapp_service.is_enabled():
        logger.warning("WhatsApp no disponible para enviar reservas_info")
        return

    message = """📅 Tus Reservas

Para ver tus reservas actuales, visita:
https://tu-dominio.com/clientes/mis-reservas/

También puedes:
• Hacer nuevas reservas
• Cancelar reservas existentes
• Ver historial de citas

¿Necesitas ayuda con algo específico? 🤔"""
    
    if hasattr(whatsapp_service, "send_custom_message"):
        whatsapp_service.send_custom_message(to_number, message)
    else:
        whatsapp_service.send_text_message(to_number, message)

def send_cancel_instructions(to_number):
    """Envía instrucciones para cancelar"""
    whatsapp_service = get_whatsapp_service()
    if not whatsapp_service or not whatsapp_service.is_enabled():
        logger.warning("WhatsApp no disponible para enviar cancel_instructions")
        return

    message = """❌ Cancelar Reserva

Para cancelar una reserva:

1. Ve a "Mis Reservas" en nuestra web
2. Encuentra la reserva que quieres cancelar
3. Haz clic en "Cancelar"
4. Confirma la cancelación

O escribe "ayuda" para más opciones.

¿Te ayudo con algo más? 😊"""
    
    if hasattr(whatsapp_service, "send_custom_message"):
        whatsapp_service.send_custom_message(to_number, message)
    else:
        whatsapp_service.send_text_message(to_number, message)

def send_new_reservation_info(to_number):
    """Envía información para nuevas reservas"""
    whatsapp_service = get_whatsapp_service()
    if not whatsapp_service or not whatsapp_service.is_enabled():
        logger.warning("WhatsApp no disponible para enviar new_reservation_info")
        return

    message = """🆕 Nueva Reserva

Para hacer una nueva reserva:

1. Visita: https://tu-dominio.com/
2. Busca el negocio que te interesa
3. Selecciona fecha y hora
4. Confirma tu reserva

¡Es rápido y fácil! ⚡

¿Necesitas ayuda? 😊"""
    
    if hasattr(whatsapp_service, "send_custom_message"):
        whatsapp_service.send_custom_message(to_number, message)
    else:
        whatsapp_service.send_text_message(to_number, message)

def send_contact_info(to_number):
    """Envía información de contacto"""
    whatsapp_service = get_whatsapp_service()
    if not whatsapp_service or not whatsapp_service.is_enabled():
        logger.warning("WhatsApp no disponible para enviar contact_info")
        return

    message = """📞 Contacto

¿Necesitas ayuda personalizada?

• Email: soporte@tu-dominio.com
• Teléfono: +57 300 123 4567
• Horario: Lunes a Viernes 8AM-6PM

¡Estamos aquí para ayudarte! 😊"""
    
    if hasattr(whatsapp_service, "send_custom_message"):
        whatsapp_service.send_custom_message(to_number, message)
    else:
        whatsapp_service.send_text_message(to_number, message)

def send_default_response(to_number):
    """Envía respuesta por defecto"""
    whatsapp_service = get_whatsapp_service()
    if not whatsapp_service or not whatsapp_service.is_enabled():
        logger.warning("WhatsApp no disponible para enviar default_response")
        return

    message = """🤔 No entiendo ese comando.

Comandos disponibles:
• "reservas" - Ver tus reservas
• "ayuda" - Mostrar ayuda
• "cancelar" - Cancelar reserva

O visita nuestra web para más opciones.

¿Necesitas ayuda? 😊"""
    
    if hasattr(whatsapp_service, "send_custom_message"):
        whatsapp_service.send_custom_message(to_number, message)
    else:
        whatsapp_service.send_text_message(to_number, message)