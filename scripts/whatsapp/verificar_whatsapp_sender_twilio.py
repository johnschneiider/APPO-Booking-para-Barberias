#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar el estado específico del WhatsApp Sender en Twilio
"""

import os
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

from django.conf import settings
from twilio.rest import Client
from twilio.base.exceptions import TwilioException

print("="*60)
print("VERIFICANDO WHATSAPP SENDER EN TWILIO")
print("="*60)

account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
whatsapp_number = getattr(settings, 'TWILIO_WHATSAPP_NUMBER', None)

if not account_sid or not auth_token or not whatsapp_number:
    print("[ERROR] Configuracion incompleta")
    exit(1)

print(f"\nAccount SID: {account_sid[:20]}...")
print(f"WhatsApp Number: {whatsapp_number}")

try:
    client = Client(account_sid, auth_token)
    
    # Limpiar el número (sin whatsapp: y sin +)
    clean_number = whatsapp_number.replace('whatsapp:', '').replace('+', '')
    
    print(f"\nBuscando WhatsApp Sender: {clean_number}")
    print("\n" + "-"*60)
    print("INFORMACION DEL WHATSAPP SENDER:")
    print("-"*60)
    
    # Intentar enviar un mensaje de prueba para ver el error específico
    print("\n[TEST] Intentando enviar mensaje de prueba para detectar estado...")
    
    try:
        # Intentar crear un mensaje simple para ver qué error devuelve
        from clientes.utils import get_whatsapp_service
        
        whatsapp_service = get_whatsapp_service()
        if not whatsapp_service or not whatsapp_service.is_enabled():
            print("[ERROR] WhatsApp service no disponible")
            exit(1)
        
        # Intentar enviar un mensaje de prueba a un número de prueba
        # (esto fallará si está deshabilitado, pero nos dará el error específico)
        print("Enviando mensaje de prueba a numero de prueba (esperado: fallo)...")
        
        resultado = whatsapp_service.send_template_message(
            to_phone='573000000000',  # Número de prueba (probablemente no existe)
            template_name=whatsapp_service.config.get('TEMPLATES', {}).get('texto_libre', ''),
            variables={'1': 'Test'}
        )
        
        print(f"Resultado: {resultado}")
        
        if resultado.get('success'):
            print("[OK] El sender acepta mensajes (aunque el numero puede ser invalido)")
        else:
            error_code = resultado.get('error_code')
            error_msg = resultado.get('error', '')
            
            print(f"[ERROR] Error al enviar: {error_msg}")
            if error_code:
                print(f"Error Code: {error_code}")
                
                if error_code == '63112':
                    print("\n[CRITICO] Error 63112: Meta deshabilito el WABA/sender")
                    print("El sender +15558371742 esta DESHABILITADO por Meta.")
                    print("\nACCIONES NECESARIAS:")
                    print("1. Ve a: https://console.twilio.com/us1/develop/sms/senders")
                    print("2. Busca el numero +15558371742")
                    print("3. Si dice 'Disabled by Meta', necesitas:")
                    print("   - Verificar el estado en Meta Business Manager")
                    print("   - Contactar a Meta Support para reactivar")
                    print("   - O crear un nuevo WhatsApp Sender")
                elif error_code == '21211':
                    print("[INFO] Error 21211: Numero invalido (esperado en este test)")
                else:
                    print(f"[PROBLEMA] Error desconocido: {error_code}")
    except Exception as e:
        print(f"[ERROR] Error en prueba: {e}")
        import traceback
        traceback.print_exc()
    
    # Verificar mensajes recientes para ver estados
    print("\n" + "-"*60)
    print("ULTIMOS MENSAJES ENVIADOS (para ver estados):")
    print("-"*60)
    
    try:
        messages = client.messages.list(limit=10, from_=whatsapp_number)
        if messages:
            count = 0
            for msg in messages:
                status = msg.status
                error_code = msg.error_code
                error_message = msg.error_message
                
                if status in ['failed', 'undelivered'] or error_code:
                    count += 1
                    print(f"\n  [{count}] Message SID: {msg.sid}")
                    print(f"      To: {msg.to}")
                    print(f"      Status: {status}")
                    print(f"      Date: {msg.date_created}")
                    
                    if error_code:
                        print(f"      Error Code: {error_code}")
                        print(f"      Error Message: {error_message}")
                        
                        if error_code == 63112:
                            print(f"      [CRITICO] Meta deshabilito el sender")
                        elif error_code == 63016:
                            print(f"      [PROBLEMA] Template o ventana 24h")
                    
                    if count >= 5:
                        break
            
            if count == 0:
                print("  No hay mensajes fallidos recientes (eso es bueno)")
        else:
            print("  No hay mensajes recientes")
    except TwilioException as e:
        print(f"  [ERROR] No se pudieron listar mensajes: {e}")
    
    print("\n" + "="*60)
    print("RECOMENDACIONES:")
    print("="*60)
    print("1. Ve manualmente a: https://console.twilio.com/us1/develop/sms/senders")
    print("2. Busca el numero +15558371742 en la lista de WhatsApp Senders")
    print("3. Revisa el estado:")
    print("   - 'Online' = OK")
    print("   - 'Offline' o 'Disabled by Meta' = PROBLEMA (error 63112)")
    print("4. Si esta deshabilitado, revisa Meta Business Manager:")
    print("   - https://business.facebook.com/wa/manage/")
    print("   - Busca el WABA 'Appo' y verifica el estado del numero")
    
except TwilioException as e:
    print(f"\n[ERROR] Error de Twilio: {e}")
except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
