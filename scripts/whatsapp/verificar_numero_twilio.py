#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar el estado del número de WhatsApp en Twilio
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
print("VERIFICANDO ESTADO DEL NUMERO EN TWILIO")
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
    
    # Limpiar el número (sin whatsapp:)
    clean_number = whatsapp_number.replace('whatsapp:', '').replace('+', '')
    
    print(f"\nBuscando numero: {clean_number}")
    
    # Listar todos los números de WhatsApp en la cuenta
    print("\n" + "-"*60)
    print("NUMEROS DE WHATSAPP EN TU CUENTA:")
    print("-"*60)
    
    try:
        # Intentar obtener información del sender
        # Twilio tiene una API para obtener información de WhatsApp senders
        senders = client.messaging.v1.services.list()
        
        whatsapp_senders = []
        for service in senders:
            # Buscar números en el servicio
            try:
                phone_numbers = client.messaging.v1.services(service.sid).phone_numbers.list()
                for pn in phone_numbers:
                    whatsapp_senders.append({
                        'service_sid': service.sid,
                        'service_name': service.friendly_name,
                        'phone_number': pn.phone_number,
                        'phone_number_sid': pn.sid
                    })
            except:
                pass
        
        if whatsapp_senders:
            for sender in whatsapp_senders:
                print(f"  - {sender['phone_number']}")
                print(f"    Service: {sender['service_name']} ({sender['service_sid']})")
        else:
            print("  No se encontraron numeros en servicios de messaging")
            
    except TwilioException as e:
        print(f"  [INFO] No se pudieron listar servicios: {e}")
    
    # Verificar mensajes recientes para ver el estado
    print("\n" + "-"*60)
    print("MENSAJES RECIENTES (para ver estados):")
    print("-"*60)
    
    try:
        messages = client.messages.list(limit=5, from_=whatsapp_number)
        if messages:
            for msg in messages:
                status = msg.status
                error_code = msg.error_code
                error_message = msg.error_message
                print(f"\n  Message SID: {msg.sid}")
                print(f"  To: {msg.to}")
                print(f"  Status: {status}")
                if error_code:
                    print(f"  Error Code: {error_code}")
                    print(f"  Error Message: {error_message}")
                    
                    if error_code == 63112:
                        print(f"  [CRITICO] Meta deshabilito el sender/WABA")
                    elif error_code == 63016:
                        print(f"  [PROBLEMA] Template o ventana 24h")
                print(f"  Date Created: {msg.date_created}")
        else:
            print("  No hay mensajes recientes")
    except TwilioException as e:
        print(f"  [ERROR] No se pudieron listar mensajes: {e}")
    
    # Verificar información del número directamente
    print("\n" + "-"*60)
    print("VERIFICACION DIRECTA:")
    print("-"*60)
    print(f"\nPara verificar el estado completo del numero {whatsapp_number}:")
    print(f"1. Ve a: https://console.twilio.com/us1/develop/sms/senders")
    print(f"2. Busca el numero {whatsapp_number}")
    print(f"3. Revisa el estado: 'Online', 'Offline', 'Disabled', etc.")
    print(f"\nSi dice 'Disabled by Meta' o 'Offline', ese es el problema.")
    print(f"Necesitas reactivar el sender desde Twilio o verificar en Meta WhatsApp Manager.")
    
except TwilioException as e:
    print(f"\n[ERROR] Error de Twilio: {e}")
except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
