#!/usr/bin/env python
"""
Script para verificar la configuración de WhatsApp
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

from django.conf import settings
from clientes.utils import get_whatsapp_service

import sys
import io

# Configurar stdout para UTF-8 (soporte emojis en Windows)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*60)
print("VERIFICANDO CONFIGURACION DE WHATSAPP")
print("="*60)

# Verificar variables de entorno
print("\nVariables de configuracion:")
print(f"   TWILIO_ACCOUNT_SID: {getattr(settings, 'TWILIO_ACCOUNT_SID', 'NO CONFIGURADO')[:20]}...")
print(f"   TWILIO_AUTH_TOKEN: {'[OK] Configurado' if getattr(settings, 'TWILIO_AUTH_TOKEN', None) else '[ERROR] NO CONFIGURADO'}")
print(f"   TWILIO_WHATSAPP_NUMBER: {getattr(settings, 'TWILIO_WHATSAPP_NUMBER', 'NO CONFIGURADO')}")
print(f"   TWILIO_TEMPLATE_TEXTO_LIBRE: {getattr(settings, 'TWILIO_TEMPLATE_TEXTO_LIBRE', 'NO CONFIGURADO')}")
print(f"   TWILIO_TEMPLATE_RECORDATORIO_DIA_ANTES: {getattr(settings, 'TWILIO_TEMPLATE_RECORDATORIO_DIA_ANTES', 'NO CONFIGURADO')}")
print(f"   TWILIO_TEMPLATE_RECORDATORIO_TRES_HORAS: {getattr(settings, 'TWILIO_TEMPLATE_RECORDATORIO_TRES_HORAS', 'NO CONFIGURADO')}")

# Verificar servicio
print("\nEstado del servicio WhatsApp:")
whatsapp_service = get_whatsapp_service()
if whatsapp_service:
    print(f"   Servicio: {whatsapp_service.__class__.__name__}")
    print(f"   Habilitado: {'[OK] SI' if whatsapp_service.is_enabled() else '[ERROR] NO'}")
    
    if hasattr(whatsapp_service, 'whatsapp_number'):
        print(f"   Numero WhatsApp: {whatsapp_service.whatsapp_number}")
    
    if hasattr(whatsapp_service, 'config'):
        templates = whatsapp_service.config.get('TEMPLATES', {})
        print(f"\n   Templates configurados:")
        for key, sid in templates.items():
            status = "[OK]" if sid else "[ERROR] NO CONFIGURADO"
            print(f"      {key}: {sid if sid else 'NO CONFIGURADO'} {status}")
else:
    print("   [ERROR] No se pudo inicializar el servicio WhatsApp")

print("\n" + "="*60)
