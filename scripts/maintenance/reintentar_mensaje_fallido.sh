#!/bin/bash
# Script para reintentar mensajes fallidos de WhatsApp

cd /var/www/appo.com.co
source venv/bin/activate

echo "🔄 Reintentando mensajes fallidos..."
echo ""

python manage.py shell << 'PYEOF'
from fidelizacion.models import MensajeFidelizacion, EstadoMensaje
from django.utils import timezone
from clientes.whatsapp_service import whatsapp_service

# Verificar que WhatsApp esté habilitado
if not whatsapp_service.is_enabled():
    print("❌ WhatsApp NO está habilitado")
    print("   Verifica las credenciales de Twilio")
    exit(1)

print("✅ WhatsApp está habilitado")
print("")

# Buscar mensajes fallidos
mensajes_fallidos = MensajeFidelizacion.objects.filter(estado=EstadoMensaje.FALLIDO)

print(f"📨 Mensajes fallidos encontrados: {mensajes_fallidos.count()}")

if mensajes_fallidos.exists():
    for mensaje in mensajes_fallidos:
        print(f"\n🔄 Reintentando mensaje {mensaje.id}:")
        print(f"   Tipo: {mensaje.get_tipo_display()}")
        print(f"   Destinatario: {mensaje.destinatario.username}")
        print(f"   Teléfono: {mensaje.destinatario.telefono or '❌ NO CONFIGURADO'}")
        
        if mensaje.destinatario.telefono:
            # Cambiar estado a PROGRAMADO para que el loop lo procese
            mensaje.estado = EstadoMensaje.PROGRAMADO
            mensaje.intentos_envio = 0
            mensaje.error_mensaje = None
            mensaje.fecha_programada = timezone.now()
            mensaje.save()
            print(f"   ✅ Mensaje marcado para reenvío")
        else:
            print(f"   ❌ El destinatario no tiene teléfono configurado")
    
    print(f"\n✅ {mensajes_fallidos.count()} mensaje(s) marcado(s) para reenvío")
    print("   El loop los procesará en los próximos 60 segundos")
else:
    print("   No hay mensajes fallidos para reintentar")
PYEOF

echo ""
echo "⏳ Esperando 60 segundos para que el loop procese los mensajes..."
sleep 60

echo ""
echo "📋 Verificando estado de los mensajes:"
python manage.py shell << 'PYEOF'
from fidelizacion.models import MensajeFidelizacion, EstadoMensaje

enviados = MensajeFidelizacion.objects.filter(estado=EstadoMensaje.ENVIADO).count()
pendientes = MensajeFidelizacion.objects.filter(estado__in=[EstadoMensaje.PROGRAMADO, EstadoMensaje.PENDIENTE]).count()
fallidos = MensajeFidelizacion.objects.filter(estado=EstadoMensaje.FALLIDO).count()

print(f"✅ Mensajes enviados: {enviados}")
print(f"⏳ Mensajes pendientes: {pendientes}")
print(f"❌ Mensajes fallidos: {fallidos}")

if fallidos > 0:
    print("\n⚠️ Aún hay mensajes fallidos. Revisa los logs:")
    print("   sudo journalctl -u appo -n 100 | grep -i 'whatsapp\|twilio\|fidelizacion'")
PYEOF

