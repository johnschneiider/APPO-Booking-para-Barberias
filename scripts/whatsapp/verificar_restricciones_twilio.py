#!/usr/bin/env python
"""
Script para verificar restricciones de Twilio
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

def verificar_restricciones_twilio():
    """Verificar restricciones de Twilio"""
    print("🔍 Verificando restricciones de Twilio...")
    
    try:
        from twilio.rest import Client
        from django.conf import settings
        
        # Crear cliente de Twilio
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        # Obtener información de la cuenta
        account = client.api.accounts(settings.TWILIO_ACCOUNT_SID).fetch()
        print(f"✅ Account Status: {account.status}")
        print(f"✅ Account Type: {account.type}")
        
        # Obtener información del número de WhatsApp
        phone_number = client.messaging.v1.services(settings.TWILIO_WHATSAPP_NUMBER).fetch()
        print(f"✅ WhatsApp Number Status: {phone_number.status}")
        
        # Verificar mensajes recientes
        messages = client.messages.list(limit=5)
        print(f"\n📱 Últimos 5 mensajes:")
        for msg in messages:
            print(f"   - SID: {msg.sid}")
            print(f"     Estado: {msg.status}")
            print(f"     Para: {msg.to}")
            print(f"     De: {msg.from_}")
            print(f"     Creado: {msg.date_created}")
            print(f"     Error: {getattr(msg, 'error_code', 'N/A')}")
            print(f"     Error Message: {getattr(msg, 'error_message', 'N/A')}")
            print()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_restricciones_twilio()
