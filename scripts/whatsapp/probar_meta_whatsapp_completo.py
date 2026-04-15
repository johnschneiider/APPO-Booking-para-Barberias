#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script completo para probar Meta WhatsApp API con la configuración del .env
"""

import os
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from dotenv import load_dotenv
load_dotenv()

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

from django.conf import settings
from clientes.utils import get_whatsapp_service
from clientes.meta_whatsapp_service import meta_whatsapp_service

print("="*60)
print("PRUEBA COMPLETA DE META WHATSAPP API")
print("="*60)

# Verificar configuración
print("\n1. VERIFICANDO CONFIGURACION...")
print("-"*60)

print(f"META_WHATSAPP_ENABLED: {getattr(settings, 'META_WHATSAPP_ENABLED', False)}")
print(f"META_WHATSAPP_PHONE_NUMBER_ID: {getattr(settings, 'META_WHATSAPP_PHONE_NUMBER_ID', 'NO CONFIGURADO')}")
print(f"META_WHATSAPP_ACCESS_TOKEN: {'CONFIGURADO' if getattr(settings, 'META_WHATSAPP_ACCESS_TOKEN', '') else 'NO CONFIGURADO'}")
print(f"META_WHATSAPP_API_VERSION: {getattr(settings, 'META_WHATSAPP_API_VERSION', 'v21.0')}")

# Verificar servicio
print("\n2. VERIFICANDO SERVICIO...")
print("-"*60)

whatsapp_service = get_whatsapp_service()
if whatsapp_service:
    print(f"Servicio: {whatsapp_service.__class__.__name__}")
    print(f"Habilitado: {whatsapp_service.is_enabled()}")
    
    if hasattr(whatsapp_service, 'phone_number_id'):
        print(f"Phone Number ID: {whatsapp_service.phone_number_id}")
    if hasattr(whatsapp_service, 'api_version'):
        print(f"API Version: {whatsapp_service.api_version}")
    if hasattr(whatsapp_service, 'templates'):
        print(f"Templates configurados: {len(whatsapp_service.templates)}")
        for key, name in whatsapp_service.templates.items():
            print(f"  {key}: {name}")
else:
    print("[ERROR] No se pudo obtener el servicio de WhatsApp")
    sys.exit(1)

if not whatsapp_service.is_enabled():
    print("[ERROR] WhatsApp service no está habilitado o configurado correctamente")
    sys.exit(1)

# Prueba 1: Enviar con template "appo" (el que ya está creado)
print("\n3. PRUEBA 1: Enviando mensaje con template 'appo'...")
print("-"*60)

numero_prueba = "573117451274"  # Tu número

resultado1 = whatsapp_service.send_template_message(
    to_phone=numero_prueba,
    template_name="appo",
    language_code="es",
    components=[{
        "type": "body",
        "parameters": [
            {"type": "text", "text": "Prueba de Meta WhatsApp API - Template appo funcionando!"}
        ]
    }]
)

print(f"Resultado: {resultado1}")
if resultado1.get('success'):
    message_id = resultado1.get('message_id')
    print(f"[OK] Mensaje enviado exitosamente!")
    print(f"Message ID: {message_id}")
    
    # Esperar un poco y verificar estado
    import time
    print("\nEsperando 3 segundos para verificar estado...")
    time.sleep(3)
    
    if message_id:
        status = whatsapp_service.get_message_status(message_id)
        if status and status.get('success'):
            data = status.get('data', {})
            print(f"Estado del mensaje: {data.get('status', 'unknown')}")
else:
    print(f"[ERROR] No se pudo enviar: {resultado1.get('error')}")

# Prueba 2: Probar con los templates de recordatorios (aunque estén en revisión)
print("\n4. PRUEBA 2: Probando template de recordatorio_dia_antes...")
print("-"*60)

# Obtener nombre del template
template_name = getattr(whatsapp_service, 'templates', {}).get('recordatorio_dia_antes', 'recordatorio_dia_antes_appo')
print(f"Template name: {template_name}")

# Preparar variables de prueba
components = [{
    "type": "body",
    "parameters": [
        {"type": "text", "text": "Juan Perez"},      # {{1}} cliente
        {"type": "text", "text": "Salon Bella"},     # {{2}} negocio
        {"type": "text", "text": "Corte de pelo"},   # {{3}} servicio
        {"type": "text", "text": "15 de enero de 2026"},  # {{4}} fecha
        {"type": "text", "text": "10:00"},           # {{5}} hora
        {"type": "text", "text": "Calle 123"},       # {{6}} direccion
        {"type": "text", "text": "3001234567"},      # {{7}} telefono
        {"type": "text", "text": "https://appo.com.co/editar/123"},  # {{8}} url
    ]
}]

resultado2 = whatsapp_service.send_template_message(
    to_phone=numero_prueba,
    template_name=template_name,
    language_code="es",
    components=components
)

print(f"Resultado: {resultado2}")
if resultado2.get('success'):
    message_id = resultado2.get('message_id')
    print(f"[OK] Mensaje de recordatorio enviado exitosamente!")
    print(f"Message ID: {message_id}")
else:
    error = resultado2.get('error', 'Error desconocido')
    print(f"[ERROR] No se pudo enviar recordatorio: {error}")
    
    # Si es porque el template está en revisión, es normal
    if 'template' in error.lower() or 'pending' in error.lower() or 'review' in error.lower():
        print("[INFO] Esto es normal - el template está en revisión en Meta")

# Prueba 3: Verificar que el servicio Meta esté priorizado sobre Twilio
print("\n5. VERIFICANDO PRIORIDAD DE SERVICIOS...")
print("-"*60)

print(f"Servicio obtenido: {whatsapp_service.__class__.__name__}")
if whatsapp_service.__class__.__name__ == 'MetaWhatsAppService':
    print("[OK] Meta WhatsApp está siendo usado (correcto)")
elif whatsapp_service.__class__.__name__ == 'TwilioWhatsAppService':
    print("[ADVERTENCIA] Twilio está siendo usado en lugar de Meta")
    print("Verifica que META_WHATSAPP_ENABLED=True en .env")

# Prueba 4: Probar desde el código de Django (simulando una reserva)
print("\n6. PRUEBA 4: Probando método send_recordatorio_dia_antes completo...")
print("-"*60)

try:
    from clientes.models import Reserva
    from negocios.models import Negocio
    from django.contrib.auth import get_user_model
    from datetime import date, time, timedelta
    from django.utils import timezone
    
    # Intentar obtener o crear datos de prueba
    User = get_user_model()
    
    # Buscar un cliente con teléfono
    cliente = User.objects.filter(tipo='cliente', telefono__isnull=False).first()
    
    if not cliente:
        print("  [INFO] No hay clientes con teléfono en la BD. Creando uno de prueba...")
        cliente, _ = User.objects.get_or_create(
            username='cliente_prueba_meta',
            defaults={
                'email': 'cliente_meta@test.com',
                'tipo': 'cliente',
                'telefono': numero_prueba
            }
        )
        if not cliente.telefono:
            cliente.telefono = numero_prueba
            cliente.save()
    
    print(f"  Cliente: {cliente.username} - {cliente.telefono}")
    
    # Buscar un negocio
    negocio = Negocio.objects.first()
    if not negocio:
        print("  [INFO] No hay negocios en la BD. Usando método directo.")
    else:
        print(f"  Negocio: {negocio.nombre}")
        
        # Crear una reserva de prueba para mañana
        mañana = timezone.now().date() + timedelta(days=1)
        reserva, _ = Reserva.objects.get_or_create(
            cliente=cliente,
            peluquero=negocio,
            fecha=mañana,
            hora_inicio=time(10, 0),
            defaults={
                'hora_fin': time(11, 0),
                'estado': 'confirmado',
                'recordatorio_dia_enviado': False
            }
        )
        
        print(f"  Reserva creada: ID {reserva.id} para {reserva.fecha}")
        
        # Probar envío de recordatorio
        resultado3 = whatsapp_service.send_recordatorio_dia_antes(reserva)
        
        print(f"\n  Resultado: {resultado3}")
        if resultado3.get('success'):
            print(f"  [OK] Recordatorio enviado exitosamente desde método Django!")
            print(f"  Message ID: {resultado3.get('message_id')}")
        else:
            print(f"  [ERROR] {resultado3.get('error')}")
            if 'template' in resultado3.get('error', '').lower():
                print("  [INFO] Normal si el template está en revisión")

except Exception as e:
    print(f"  [ERROR] Excepción al probar método Django: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("RESUMEN DE PRUEBAS")
print("="*60)

if whatsapp_service.__class__.__name__ == 'MetaWhatsAppService' and whatsapp_service.is_enabled():
    print("[OK] Meta WhatsApp API está configurado y habilitado")
    print("[OK] Token cargado correctamente")
    print(f"[OK] Phone Number ID: {getattr(whatsapp_service, 'phone_number_id', 'N/A')}")
    
    if resultado1.get('success'):
        print("[OK] Template 'appo' funcionó correctamente")
    else:
        print(f"[ADVERTENCIA] Template 'appo' falló: {resultado1.get('error')}")
    
    if resultado2.get('success'):
        print("[OK] Template de recordatorios funcionó")
    else:
        print("[INFO] Template de recordatorios puede estar en revisión (normal)")
else:
    print("[ERROR] Hay problemas con la configuración de Meta WhatsApp")

print("\n" + "="*60)
print("PRUEBAS COMPLETADAS")
print("="*60)
