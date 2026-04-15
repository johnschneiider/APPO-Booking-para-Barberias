#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

from clientes.twilio_whatsapp_service import twilio_whatsapp_service

print("Probando WhatsApp con 3117451274...")
resultado = twilio_whatsapp_service.send_text_message('3117451274', '¡Hola! Prueba desde Melissa 🚀')
print(f"Resultado: {resultado}")

if resultado.get('success'):
    print("¡Mensaje enviado!")
    message_id = resultado.get('message_id')
    print(f"Message ID: {message_id}")
    
    # Verificar estado
    import time
    time.sleep(3)
    estado = twilio_whatsapp_service.get_message_status(message_id)
    print(f"Estado: {estado}")
else:
    print(f"Error: {resultado.get('error')}")