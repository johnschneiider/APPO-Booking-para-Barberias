#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para probar que los templates esten configurados y funcionen
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

from clientes.utils import get_whatsapp_service

print("="*60)
print("VERIFICANDO TEMPLATES CONFIGURADOS")
print("="*60)

whatsapp_service = get_whatsapp_service()
if not whatsapp_service or not whatsapp_service.is_enabled():
    print("[ERROR] WhatsApp service no disponible")
    exit(1)

print("\nTemplates configurados:")
print("-"*60)

templates_config = whatsapp_service.config.get('TEMPLATES', {})
template_keys = {
    'reserva_confirmada': 'Reserva Confirmada',
    'recordatorio_dia_antes': 'Recordatorio Dia Antes',
    'recordatorio_tres_horas': 'Recordatorio 3 Horas',
    'reserva_cancelada': 'Reserva Cancelada',
    'reserva_reagendada': 'Reserva Reagendada',
    'inasistencia': 'Inasistencia',
    'texto_libre': 'Texto Libre (Fallback)',
}

for key, desc in template_keys.items():
    sid = templates_config.get(key, '')
    if sid:
        print(f"  {desc}: {sid} [OK]")
    else:
        print(f"  {desc}: [ERROR] NO CONFIGURADO")

print("\n" + "="*60)
print("PRUEBA DE ENVIO CON TEMPLATE")
print("="*60)

# Verificar si al menos uno está configurado
template_dia = templates_config.get('recordatorio_dia_antes', '')
if template_dia:
    print(f"\nIntentando enviar con template: {template_dia}")
    print("Numero: +573117451274")
    
    variables = {
        "1": "Juan Perez",
        "2": "Salon Bella",
        "3": "Corte de pelo",
        "4": "15 de enero de 2026",
        "5": "10:00",
        "6": "Calle 123",
        "7": "3001234567",
        "8": "https://appo.com.co/editar/123",
    }
    
    resultado = whatsapp_service.send_template_message(
        to_phone='3117451274',
        template_name=template_dia,
        variables=variables
    )
    
    print(f"Resultado: {resultado}")
    
    if resultado.get('success'):
        message_sid = resultado.get('message_id')
        print(f"[OK] Mensaje creado: {message_sid}")
        print("Esperando 5 segundos para verificar estado...")
        import time
        time.sleep(5)
        
        status = whatsapp_service.get_message_status(message_sid)
        if status and status.get('success'):
            data = status.get('data', {})
            status_real = data.get('status', 'unknown')
            error_code = data.get('error_code')
            
            print(f"Estado real: {status_real}")
            if error_code:
                print(f"Error Code: {error_code}")
                if error_code == '63112':
                    print("[PROBLEMA] Meta deshabilito el sender - este es el problema principal")
                elif error_code == '63016':
                    print("[PROBLEMA] Template o ventana 24h")
    else:
        print(f"[ERROR] No se pudo enviar: {resultado.get('error')}")
else:
    print("[ERROR] Template recordatorio_dia_antes no configurado en .env")

print("\n" + "="*60)
