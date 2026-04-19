from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.conf import settings
import logging
from .utils import get_whatsapp_service

logger = logging.getLogger(__name__)


@require_GET
def whatsapp_webhook_verify(request):
    """
    Health-check / verificación del webhook.
    Twilio no requiere este handshake — se conserva como endpoint de diagnóstico.
    """
    return HttpResponse('OK - Twilio WhatsApp webhook activo', content_type='text/plain')


def verify_twilio_signature(request):
    """
    Valida la firma X-Twilio-Signature que Twilio incluye en cada POST.
    Usa RequestValidator de la librería oficial de Twilio.
    Si no hay AUTH_TOKEN configurado (desarrollo local) permite el paso con advertencia.
    """
    try:
        auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
        if not auth_token:
            logger.warning("TWILIO_AUTH_TOKEN no configurado — omitiendo validación de firma (solo desarrollo)")
            return True

        from twilio.request_validator import RequestValidator
        validator = RequestValidator(auth_token)

        # URL completa que Twilio usó
        url = request.build_absolute_uri()
        post_params = request.POST.dict()
        signature = request.headers.get('X-Twilio-Signature', '')

        valid = validator.validate(url, post_params, signature)
        if not valid:
            logger.warning(f"X-Twilio-Signature inválida para URL: {url}")
        return valid

    except Exception as e:
        logger.error(f"Error verificando firma de Twilio: {e}")
        return False


@csrf_exempt
@require_POST
def whatsapp_webhook(request):
    """
    Recibe mensajes entrantes de WhatsApp vía Twilio.

    Twilio envía POST con Content-Type: application/x-www-form-urlencoded.
    Campos principales:
      From  → 'whatsapp:+573001234567'
      To    → 'whatsapp:+15558371742'
      Body  → texto del mensaje
      MessageSid, NumMedia, etc.

    URL a configurar en Twilio Console:
      https://<tu-dominio>/clientes/whatsapp/webhook/
    """
    try:
        if not verify_twilio_signature(request):
            logger.warning("Firma de Twilio inválida — rechazando webhook")
            return HttpResponse('Unauthorized', status=401)

        # Twilio envía form-data, no JSON
        from_raw = request.POST.get('From', '')        # ej: whatsapp:+573001234567
        body_text = request.POST.get('Body', '').strip()
        message_sid = request.POST.get('MessageSid', '')
        num_media = int(request.POST.get('NumMedia', 0))

        # Limpiar prefijo 'whatsapp:'
        from_phone = from_raw.replace('whatsapp:', '').strip()

        logger.info(f"Twilio webhook recibido | from={from_phone} | sid={message_sid} | body={body_text[:60]!r}")

        if body_text:
            handle_text_message(from_phone, body_text, timestamp=None)
        elif num_media > 0:
            logger.info(f"Mensaje multimedia recibido de {from_phone} ({num_media} archivos) — no procesado")
        else:
            logger.info(f"Webhook sin body ni media de {from_phone}")

        # Twilio espera 200 OK con cuerpo vacío o TwiML
        return HttpResponse('', content_type='text/plain', status=200)

    except Exception as e:
        logger.error(f"Error procesando webhook de Twilio: {e}")
        return HttpResponse('Internal Server Error', status=500)

# process_whatsapp_message era específico de la API de Meta (formato JSON con 'type'/'text'/'button').
# Con Twilio el Body llega directamente en el POST — se procesa en whatsapp_webhook().

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