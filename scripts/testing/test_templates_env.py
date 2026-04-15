#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from dotenv import load_dotenv
load_dotenv()

print("="*60)
print("VERIFICANDO TEMPLATES EN .ENV")
print("="*60)

print("\nVariables directamente de os.getenv:")
print("-"*60)
print(f"TWILIO_TEMPLATE_RESERVA_CONFIRMADA: {os.getenv('TWILIO_TEMPLATE_RESERVA_CONFIRMADA', 'NO ENCONTRADO')}")
print(f"TWILIO_TEMPLATE_RECORDATORIO_DIA_ANTES: {os.getenv('TWILIO_TEMPLATE_RECORDATORIO_DIA_ANTES', 'NO ENCONTRADO')}")
print(f"TWILIO_TEMPLATE_RECORDATORIO_TRES_HORAS: {os.getenv('TWILIO_TEMPLATE_RECORDATORIO_TRES_HORAS', 'NO ENCONTRADO')}")
print(f"TWILIO_TEMPLATE_RESERVA_CANCELADA: {os.getenv('TWILIO_TEMPLATE_RESERVA_CANCELADA', 'NO ENCONTRADO')}")
print(f"TWILIO_TEMPLATE_RESERVA_REAGENDADA: {os.getenv('TWILIO_TEMPLATE_RESERVA_REAGENDADA', 'NO ENCONTRADO')}")
print(f"TWILIO_TEMPLATE_INASISTENCIA: {os.getenv('TWILIO_TEMPLATE_INASISTENCIA', 'NO ENCONTRADO')}")
print(f"TWILIO_TEMPLATE_TEXTO_LIBRE: {os.getenv('TWILIO_TEMPLATE_TEXTO_LIBRE', 'NO ENCONTRADO')}")

print("\n" + "="*60)
print("PROBANDO CON DJANGO")
print("="*60)

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

from django.conf import settings
from clientes.utils import get_whatsapp_service

print("\nVariables desde Django settings:")
print("-"*60)
print(f"TWILIO_TEMPLATE_RESERVA_CONFIRMADA: {getattr(settings, 'TWILIO_TEMPLATE_RESERVA_CONFIRMADA', 'NO')}")
print(f"TWILIO_TEMPLATE_RECORDATORIO_DIA_ANTES: {getattr(settings, 'TWILIO_TEMPLATE_RECORDATORIO_DIA_ANTES', 'NO')}")
print(f"TWILIO_TEMPLATE_RECORDATORIO_TRES_HORAS: {getattr(settings, 'TWILIO_TEMPLATE_RECORDATORIO_TRES_HORAS', 'NO')}")
print(f"TWILIO_TEMPLATE_RESERVA_CANCELADA: {getattr(settings, 'TWILIO_TEMPLATE_RESERVA_CANCELADA', 'NO')}")
print(f"TWILIO_TEMPLATE_RESERVA_REAGENDADA: {getattr(settings, 'TWILIO_TEMPLATE_RESERVA_REAGENDADA', 'NO')}")
print(f"TWILIO_TEMPLATE_INASISTENCIA: {getattr(settings, 'TWILIO_TEMPLATE_INASISTENCIA', 'NO')}")
print(f"TWILIO_TEMPLATE_TEXTO_LIBRE: {getattr(settings, 'TWILIO_TEMPLATE_TEXTO_LIBRE', 'NO')}")

whatsapp_service = get_whatsapp_service()
if whatsapp_service:
    print("\nTemplates cargados en servicio:")
    print("-"*60)
    templates = whatsapp_service.config.get('TEMPLATES', {})
    for key, sid in templates.items():
        status = "OK" if sid else "NO CONFIGURADO"
        print(f"  {key}: {sid if sid else '(vacío)'} [{status}]")
else:
    print("\n[ERROR] WhatsApp service no disponible")

print("\n" + "="*60)
