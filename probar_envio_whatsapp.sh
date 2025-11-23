#!/bin/bash
# Script para probar el envío de un mensaje de WhatsApp

cd /var/www/appo.com.co
source venv/bin/activate

echo "🧪 Probando envío de WhatsApp..."
echo ""

python manage.py shell << 'PYEOF'
from clientes.whatsapp_service import whatsapp_service
from django.conf import settings
from fidelizacion.models import MensajeFidelizacion, EstadoMensaje
from django.utils import timezone

print("📋 Configuración de Twilio:")
print(f"   Account SID: {settings.TWILIO_ACCOUNT_SID[:10]}..." if settings.TWILIO_ACCOUNT_SID and len(settings.TWILIO_ACCOUNT_SID) > 10 else f"   Account SID: {settings.TWILIO_ACCOUNT_SID or '❌ NO CONFIGURADO'}")
print(f"   Auth Token: {'✅ Configurado' if settings.TWILIO_AUTH_TOKEN and settings.TWILIO_AUTH_TOKEN != 'tu-twilio-auth-token' else '❌ NO CONFIGURADO'}")
print(f"   WhatsApp Number: {settings.TWILIO_WHATSAPP_NUMBER}")
print(f"   WhatsApp Enabled: {settings.TWILIO_WHATSAPP_ENABLED}")

print("\n🔍 Verificando servicio de WhatsApp:")
enabled = whatsapp_service.is_enabled()
print(f"   ¿WhatsApp habilitado?: {enabled}")

if not enabled:
    print("\n❌ WhatsApp NO está habilitado")
    print("\n🔧 Verifica:")
    if not settings.TWILIO_ACCOUNT_SID or settings.TWILIO_ACCOUNT_SID == '':
        print("   ❌ TWILIO_ACCOUNT_SID no está configurado")
    if not settings.TWILIO_AUTH_TOKEN or settings.TWILIO_AUTH_TOKEN == '' or settings.TWILIO_AUTH_TOKEN == 'tu-twilio-auth-token':
        print("   ❌ TWILIO_AUTH_TOKEN no está configurado o es placeholder")
    print("   1. Verifica que las variables estén en .env")
    print("   2. Reinicia el servicio: sudo systemctl restart appo")
    exit(1)

print("\n✅ WhatsApp está configurado correctamente")

# Buscar un mensaje fallido para reintentar
print("\n📨 Buscando mensajes fallidos para reintentar...")
mensaje_fallido = MensajeFidelizacion.objects.filter(estado=EstadoMensaje.FALLIDO).first()

if mensaje_fallido:
    print(f"   Encontrado mensaje fallido ID: {mensaje_fallido.id}")
    print(f"   Tipo: {mensaje_fallido.get_tipo_display()}")
    print(f"   Destinatario: {mensaje_fallido.destinatario.username}")
    print(f"   Teléfono: {mensaje_fallido.destinatario.telefono or '❌ NO CONFIGURADO'}")
    
    if mensaje_fallido.destinatario.telefono:
        print(f"\n🔄 Intentando reenviar mensaje...")
        # Cambiar estado a PROGRAMADO para que el loop lo procese
        mensaje_fallido.estado = EstadoMensaje.PROGRAMADO
        mensaje_fallido.intentos_envio = 0
        mensaje_fallido.error_mensaje = None
        mensaje_fallido.fecha_programada = timezone.now()
        mensaje_fallido.save()
        print(f"   ✅ Mensaje marcado para reenvío")
        print(f"   El loop lo procesará en los próximos 60 segundos")
    else:
        print(f"   ❌ El destinatario no tiene teléfono configurado")
else:
    print("   No hay mensajes fallidos")
    print("\n💡 Para probar, crea una nueva reserva o espera a que se procesen los mensajes programados")
PYEOF

