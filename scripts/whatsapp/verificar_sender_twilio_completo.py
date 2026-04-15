#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar estado completo del WhatsApp Sender en Twilio
"""

import os
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

from django.conf import settings
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
import json

print("="*60)
print("VERIFICACION COMPLETA DE WHATSAPP SENDER")
print("="*60)

account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
whatsapp_number = getattr(settings, 'TWILIO_WHATSAPP_NUMBER', None)

if not account_sid or not auth_token:
    print("[ERROR] Credenciales de Twilio no configuradas")
    exit(1)

print(f"\nAccount SID: {account_sid[:20]}...")
print(f"WhatsApp Number: {whatsapp_number}")

try:
    client = Client(account_sid, auth_token)
    
    # Limpiar número
    clean_number = whatsapp_number.replace('whatsapp:', '').replace('+', '')
    
    print("\n" + "-"*60)
    print("MENSAJES RECIENTES (ultimos 10):")
    print("-"*60)
    
    try:
        messages = client.messages.list(limit=10, from_=whatsapp_number)
        
        errores_63112 = 0
        errores_63016 = 0
        otros_errores = 0
        exitosos = 0
        
        for msg in messages:
            status = msg.status
            error_code = msg.error_code
            error_message = msg.error_message
            
            if status in ['failed', 'undelivered']:
                if error_code == 63112:
                    errores_63112 += 1
                elif error_code == 63016:
                    errores_63016 += 1
                else:
                    otros_errores += 1
            elif status in ['delivered', 'read']:
                exitosos += 1
            
            # Mostrar detalles de mensajes fallidos
            if status in ['failed', 'undelivered'] and error_code:
                print(f"\n[{status.upper()}] Message SID: {msg.sid}")
                print(f"  To: {msg.to}")
                print(f"  Date: {msg.date_created}")
                print(f"  Error Code: {error_code}")
                if error_message:
                    print(f"  Error Message: {error_message}")
                
                if error_code == 63112:
                    print(f"  [CRITICO] Meta deshabilito el sender/WABA")
                elif error_code == 63016:
                    print(f"  [PROBLEMA] Template o ventana 24h")
        
        print(f"\n" + "-"*60)
        print(f"RESUMEN DE ULTIMOS 10 MENSAJES:")
        print(f"  Exitosos (delivered/read): {exitosos}")
        print(f"  Error 63112 (Meta bloqueo): {errores_63112}")
        print(f"  Error 63016 (Template/ventana): {errores_63016}")
        print(f"  Otros errores: {otros_errores}")
        
        if errores_63112 > 0:
            print(f"\n[CRITICO] {errores_63112} mensajes fallaron por error 63112")
            print(f"Esto confirma que Meta deshabilito el sender/WABA")
            print(f"\nACCION REQUERIDA:")
            print(f"1. Ve a: https://console.twilio.com/us1/develop/sms/senders/whatsapp-senders")
            print(f"2. Busca el numero {whatsapp_number}")
            print(f"3. Si dice 'Disabled by Meta' o 'Offline', necesitas reactivarlo")
            print(f"4. Contacta a Twilio Support con los Message SIDs fallidos")
        
        if not messages:
            print("  No hay mensajes recientes")
            
    except TwilioException as e:
        print(f"  [ERROR] No se pudieron listar mensajes: {e}")
    
    # Verificar templates
    print("\n" + "-"*60)
    print("VERIFICACION DE TEMPLATES:")
    print("-"*60)
    
    from clientes.utils import get_whatsapp_service
    ws = get_whatsapp_service()
    if ws:
        templates = ws.config.get('TEMPLATES', {})
        configurados = sum(1 for v in templates.values() if v)
        total = len(templates)
        print(f"  Templates configurados: {configurados}/{total}")
        
        for key, sid in templates.items():
            if sid:
                print(f"    {key}: {sid[:20]}... [OK]")
            else:
                print(f"    {key}: [NO CONFIGURADO]")
    else:
        print("  [ERROR] WhatsApp service no disponible")
    
    print("\n" + "="*60)
    print("CONCLUSION:")
    print("="*60)
    
    if errores_63112 > 0:
        print("[CRITICO] El problema es el error 63112 - Meta deshabilito el sender")
        print("Los templates estan bien configurados, pero Meta bloquea los envios.")
        print("\nSOLUCION:")
        print("1. Contacta a Twilio Support: https://support.twilio.com/")
        print("2. O verifica en Meta WhatsApp Manager si el numero esta activo")
        print("3. Mientras tanto, los recordatorios NO funcionaran")
    else:
        print("[OK] No hay errores 63112 en mensajes recientes")
        print("El problema puede ser otro (revisa otros errores)")
    
except TwilioException as e:
    print(f"\n[ERROR] Error de Twilio: {e}")
except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
