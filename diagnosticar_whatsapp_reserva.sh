#!/bin/bash
# Script para diagnosticar por qué no llegó la confirmación de WhatsApp

cd /var/www/appo.com.co
source venv/bin/activate

echo "🔍 Diagnóstico de WhatsApp para Reservas"
echo "=========================================="
echo ""

# 1. Verificar última reserva creada
echo "📋 1. Verificando última reserva creada..."
python manage.py shell << 'PYEOF'
from clientes.models import Reserva
from django.utils import timezone
from datetime import timedelta

# Obtener la última reserva creada en las últimas 24 horas
ultima_reserva = Reserva.objects.filter(
    fecha_creacion__gte=timezone.now() - timedelta(hours=24)
).order_by('-fecha_creacion').first()

if ultima_reserva:
    print(f"✅ Última reserva encontrada:")
    print(f"   ID: {ultima_reserva.id}")
    print(f"   Cliente: {ultima_reserva.cliente.username} ({ultima_reserva.cliente.get_full_name() or 'Sin nombre'})")
    print(f"   Teléfono: {ultima_reserva.cliente.telefono or '❌ NO CONFIGURADO'}")
    print(f"   Fecha: {ultima_reserva.fecha}")
    print(f"   Hora: {ultima_reserva.hora_inicio}")
    print(f"   Estado: {ultima_reserva.estado}")
    print(f"   Fecha creación: {ultima_reserva.fecha_creacion}")
else:
    print("⚠️ No se encontraron reservas en las últimas 24 horas")
PYEOF

echo ""
echo "📨 2. Verificando mensajes de fidelización creados..."
python manage.py shell << 'PYEOF'
from fidelizacion.models import MensajeFidelizacion, TipoMensaje
from clientes.models import Reserva
from django.utils import timezone
from datetime import timedelta

# Obtener la última reserva
ultima_reserva = Reserva.objects.filter(
    fecha_creacion__gte=timezone.now() - timedelta(hours=24)
).order_by('-fecha_creacion').first()

if ultima_reserva:
    print(f"Buscando mensajes para reserva ID: {ultima_reserva.id}")
    mensajes = MensajeFidelizacion.objects.filter(reserva=ultima_reserva)
    
    if mensajes.exists():
        print(f"✅ Se encontraron {mensajes.count()} mensajes:")
        for msg in mensajes:
            print(f"   - {msg.get_tipo_display()}: {msg.get_estado_display()}")
            print(f"     Fecha programada: {msg.fecha_programada}")
            print(f"     Fecha envío: {msg.fecha_envio or 'No enviado'}")
            if msg.error_mensaje:
                print(f"     Error: {msg.error_mensaje}")
    else:
        print("❌ NO se crearon mensajes de fidelización para esta reserva")
        print("   Esto indica que las señales no se activaron correctamente")
else:
    print("⚠️ No hay reserva reciente para verificar")
PYEOF

echo ""
echo "🔧 3. Verificando configuración de WhatsApp..."
python manage.py shell << 'PYEOF'
from clientes.whatsapp_service import whatsapp_service

print(f"¿WhatsApp habilitado?: {whatsapp_service.is_enabled()}")
if hasattr(whatsapp_service, 'account_sid'):
    print(f"Twilio Account SID: {whatsapp_service.account_sid[:10]}..." if whatsapp_service.account_sid else "No configurado")
    print(f"Twilio Phone: {whatsapp_service.phone_number or 'No configurado'}")
else:
    print("⚠️ Servicio de WhatsApp no tiene configuración visible")
PYEOF

echo ""
echo "📊 4. Verificando mensajes pendientes en la cola..."
python manage.py shell << 'PYEOF'
from fidelizacion.models import MensajeFidelizacion, EstadoMensaje
from django.utils import timezone

pendientes = MensajeFidelizacion.objects.filter(
    estado__in=[EstadoMensaje.PENDIENTE, EstadoMensaje.PROGRAMADO],
    fecha_programada__lte=timezone.now()
)

print(f"📋 Mensajes pendientes de enviar: {pendientes.count()}")
if pendientes.exists():
    print("Últimos 5 mensajes pendientes:")
    for msg in pendientes[:5]:
        print(f"   - {msg.get_tipo_display()} a {msg.destinatario.username}")
        print(f"     Estado: {msg.get_estado_display()}, Programado: {msg.fecha_programada}")

fallidos = MensajeFidelizacion.objects.filter(estado=EstadoMensaje.FALLIDO)
print(f"\n❌ Mensajes fallidos: {fallidos.count()}")
if fallidos.exists():
    print("Últimos 3 mensajes fallidos:")
    for msg in fallidos[:3]:
        print(f"   - {msg.get_tipo_display()} a {msg.destinatario.username}")
        print(f"     Error: {msg.error_mensaje}")
PYEOF

echo ""
echo "🔄 5. Verificando logs del servicio (últimos 2 minutos)..."
sudo journalctl -u appo --since "2 minutes ago" | grep -i "fidelizacion\|whatsapp\|mensaje" | tail -20

echo ""
echo "✅ Diagnóstico completado"
echo ""
echo "💡 Próximos pasos:"
echo "   1. Si el cliente no tiene teléfono: configúralo en el admin"
echo "   2. Si no se crearon mensajes: verifica que las señales estén activas"
echo "   3. Si hay mensajes pendientes: el loop debería procesarlos automáticamente"
echo "   4. Si WhatsApp no está habilitado: configura las variables TWILIO_* en .env"

