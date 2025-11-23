#!/bin/bash
# Script rápido para verificar una reserva específica

cd /var/www/appo.com.co
source venv/bin/activate

echo "🔍 Verificando última reserva y mensajes..."
echo ""

python manage.py shell << 'PYEOF'
from clientes.models import Reserva
from fidelizacion.models import MensajeFidelizacion
from django.utils import timezone
from datetime import timedelta

# Última reserva
reserva = Reserva.objects.order_by('-creado_en').first()
if reserva:
    print(f"✅ Reserva ID: {reserva.id}")
    print(f"   Cliente: {reserva.cliente.username}")
    print(f"   Teléfono: {reserva.cliente.telefono or '❌ NO CONFIGURADO'}")
    print(f"   Fecha: {reserva.fecha}")
    print(f"   Hora: {reserva.hora_inicio}")
    print(f"   Estado: {reserva.estado}")
    print(f"   Creada: {reserva.creado_en}")
    
    # Mensajes creados
    mensajes = MensajeFidelizacion.objects.filter(reserva=reserva)
    print(f"\n📨 Mensajes creados: {mensajes.count()}")
    if mensajes.exists():
        for msg in mensajes:
            print(f"   - {msg.get_tipo_display()}: {msg.get_estado_display()}")
            print(f"     Programado: {msg.fecha_programada}")
            if msg.fecha_envio:
                print(f"     Enviado: {msg.fecha_envio}")
            if msg.error_mensaje:
                print(f"     ❌ Error: {msg.error_mensaje}")
    else:
        print("   ❌ NO se crearon mensajes de fidelización")
        print("   ⚠️ Esto indica que las señales no se activaron")
else:
    print("❌ No hay reservas")
PYEOF

echo ""
echo "🔧 Verificando configuración de WhatsApp..."
python manage.py shell << 'PYEOF'
from clientes.whatsapp_service import whatsapp_service

print(f"¿WhatsApp habilitado?: {whatsapp_service.is_enabled()}")
if hasattr(whatsapp_service, 'phone_number_id'):
    print(f"Phone Number ID: {whatsapp_service.phone_number_id or 'No configurado'}")
if hasattr(whatsapp_service, 'access_token'):
    token = whatsapp_service.access_token
    print(f"Access Token: {'Configurado' if token else 'No configurado'}")
PYEOF

