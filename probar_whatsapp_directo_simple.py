#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script simple para probar envío directo de WhatsApp sin usar BD
"""

import os
import sys
import io

# Configurar stdout para UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

from clientes.utils import get_whatsapp_service
import time

numero_prueba = '3117451274'

print("="*60)
print("PRUEBA DIRECTA DE ENVIO WHATSAPP")
print("="*60)

whatsapp_service = get_whatsapp_service()
if not whatsapp_service or not whatsapp_service.is_enabled():
    print("[ERROR] WhatsApp no esta disponible o no esta habilitado")
    exit(1)

print(f"\nNumero de prueba: {numero_prueba}")
print(f"Servicio: {whatsapp_service.__class__.__name__}")
print(f"Numero WhatsApp: {whatsapp_service.whatsapp_number}")

# Probar recordatorio día antes (template)
print("\n" + "-"*60)
print("PRUEBA 1: Recordatorio Dia Antes (Template)")
print("-"*60)

template_dia_antes = whatsapp_service.config.get('TEMPLATES', {}).get('recordatorio_dia_antes', '')
if not template_dia_antes:
    print("[ERROR] Template recordatorio_dia_antes no configurado")
else:
    print(f"Template SID: {template_dia_antes}")
    
    variables = {
        "1": "Juan Perez",  # cliente
        "2": "Salon Bella",  # negocio
        "3": "Corte de pelo",  # servicio
        "4": "15 de enero de 2026",  # fecha
        "5": "10:00",  # hora
        "6": "Calle 123",  # direccion
        "7": "3001234567",  # telefono negocio
        "8": "https://appo.com.co/editar/123",  # url edicion
    }
    
    print("Enviando mensaje...")
    resultado1 = whatsapp_service.send_template_message(
        to_phone=numero_prueba,
        template_name=template_dia_antes,
        variables=variables
    )
    
    print(f"Resultado: {resultado1}")
    
    if resultado1.get('success'):
        message_sid1 = resultado1.get('message_id')
        print(f"[OK] Mensaje creado. Message SID: {message_sid1}")
        print("Esperando 3 segundos para verificar estado...")
        time.sleep(3)
        
        # Verificar estado
        status1 = whatsapp_service.get_message_status(message_sid1)
        if status1 and status1.get('success'):
            data1 = status1.get('data', {})
            status_real = data1.get('status', 'unknown')
            error_code1 = data1.get('error_code')
            error_msg1 = data1.get('error_message', '')
            
            print(f"Estado real: {status_real}")
            if error_code1:
                print(f"Error Code: {error_code1}")
                print(f"Error Message: {error_msg1}")
                
                if error_code1 == '63112':
                    print("[PROBLEMA] Meta deshabilito el WABA/sender")
                elif error_code1 == '63016':
                    print("[PROBLEMA] Template no aprobado o conversacion no iniciada")
        else:
            print(f"[ERROR] No se pudo obtener estado: {status1}")
    else:
        print(f"[ERROR] No se pudo enviar: {resultado1.get('error')}")

# Probar recordatorio 3 horas (template)
print("\n" + "-"*60)
print("PRUEBA 2: Recordatorio 3 Horas (Template)")
print("-"*60)

template_tres_horas = whatsapp_service.config.get('TEMPLATES', {}).get('recordatorio_tres_horas', '')
if not template_tres_horas:
    print("[ERROR] Template recordatorio_tres_horas no configurado")
else:
    print(f"Template SID: {template_tres_horas}")
    
    variables2 = {
        "1": "Juan Perez",  # cliente
        "2": "Salon Bella",  # negocio
        "3": "Corte de pelo",  # servicio
        "4": "15 de enero de 2026",  # fecha
        "5": "10:00",  # hora
        "6": "Calle 123",  # direccion
        "7": "3001234567",  # telefono negocio
        "8": "https://appo.com.co/editar/123",  # url edicion
        "9": "Puedes cancelar con mas de 1 hora de anticipacion",  # nota
    }
    
    print("Enviando mensaje...")
    resultado2 = whatsapp_service.send_template_message(
        to_phone=numero_prueba,
        template_name=template_tres_horas,
        variables=variables2
    )
    
    print(f"Resultado: {resultado2}")
    
    if resultado2.get('success'):
        message_sid2 = resultado2.get('message_id')
        print(f"[OK] Mensaje creado. Message SID: {message_sid2}")
        print("Esperando 3 segundos para verificar estado...")
        time.sleep(3)
        
        # Verificar estado
        status2 = whatsapp_service.get_message_status(message_sid2)
        if status2 and status2.get('success'):
            data2 = status2.get('data', {})
            status_real2 = data2.get('status', 'unknown')
            error_code2 = data2.get('error_code')
            error_msg2 = data2.get('error_message', '')
            
            print(f"Estado real: {status_real2}")
            if error_code2:
                print(f"Error Code: {error_code2}")
                print(f"Error Message: {error_msg2}")
                
                if error_code2 == '63112':
                    print("[PROBLEMA] Meta deshabilito el WABA/sender")
                elif error_code2 == '63016':
                    print("[PROBLEMA] Template no aprobado o conversacion no iniciada")
        else:
            print(f"[ERROR] No se pudo obtener estado: {status2}")
    else:
        print(f"[ERROR] No se pudo enviar: {resultado2.get('error')}")

print("\n" + "="*60)
print("FIN DE PRUEBA")
print("="*60)
