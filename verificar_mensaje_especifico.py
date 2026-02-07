#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verificar un mensaje específico que falló
"""

import os
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

from clientes.utils import get_whatsapp_service

# Message SID del último test que falló
message_sid = 'MM4d80f707a232f9740abac5942b6b2a30'

print("="*60)
print(f"VERIFICANDO MENSAJE ESPECIFICO: {message_sid}")
print("="*60)

whatsapp_service = get_whatsapp_service()
if not whatsapp_service or not whatsapp_service.is_enabled():
    print("[ERROR] WhatsApp service no disponible")
    # Reactivar si está deshabilitado
    if hasattr(whatsapp_service, 'enabled'):
        whatsapp_service.enabled = True
        print("[INFO] Reactivando servicio para verificar...")

status = whatsapp_service.get_message_status(message_sid)

if status and status.get('success'):
    data = status.get('data', {})
    status_real = data.get('status', 'unknown')
    error_code = data.get('error_code')
    error_message = data.get('error_message', '')
    
    print(f"\nEstado: {status_real}")
    print(f"To: {data.get('to', 'N/A')}")
    print(f"From: {data.get('from', 'N/A')}")
    print(f"Date Created: {data.get('date_created', 'N/A')}")
    print(f"Date Updated: {data.get('date_updated', 'N/A')}")
    
    if error_code:
        print(f"\nError Code: {error_code}")
        if error_message:
            print(f"Error Message: {error_message}")
        
        if error_code == '63112':
            print("\n[CRITICO] ERROR 63112: Meta deshabilito el WABA/sender")
            print("Esto confirma que el problema NO es de templates o codigo,")
            print("sino que Meta bloqueo el sender.")
            print("\nACCION REQUERIDA:")
            print("1. Contacta a Twilio Support para que escalen con Meta")
            print("2. O verifica en Meta WhatsApp Manager el estado del numero")
            print("3. Mientras tanto, los recordatorios NO funcionaran")
        elif error_code == '63016':
            print("\n[PROBLEMA] ERROR 63016: Template o ventana 24h")
            print("El template puede no estar aprobado o la conversacion no iniciada")
        else:
            print(f"\n[ERROR] Error desconocido: {error_code}")
    else:
        print(f"\n[OK] Sin errores reportados (status: {status_real})")
        
    if status_real in ['failed', 'undelivered']:
        print(f"\n[RESULTADO] Mensaje NO entregado (status: {status_real})")
    elif status_real == 'delivered':
        print(f"\n[RESULTADO] Mensaje entregado exitosamente")
    elif status_real == 'read':
        print(f"\n[RESULTADO] Mensaje leido por el cliente")
    elif status_real in ['queued', 'sending', 'sent']:
        print(f"\n[INFO] Mensaje en proceso (status: {status_real})")
else:
    print(f"[ERROR] No se pudo obtener estado: {status}")

print("\n" + "="*60)
