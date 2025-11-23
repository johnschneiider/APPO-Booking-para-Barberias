#!/bin/bash
# Script para probar el envío de WhatsApp con Twilio

cd /var/www/appo.com.co
source venv/bin/activate

echo "🧪 Probando envío de WhatsApp con Twilio..."
echo ""

python manage.py shell << 'PYEOF'
from clientes.whatsapp_service import whatsapp_service
from django.conf import settings

print("📋 Configuración actual:")
print(f"   Account SID: {settings.TWILIO_ACCOUNT_SID[:10]}..." if settings.TWILIO_ACCOUNT_SID else "   Account SID: ❌ NO CONFIGURADO")
print(f"   Auth Token: {'Configurado' if settings.TWILIO_AUTH_TOKEN else '❌ NO CONFIGURADO'}")
print(f"   WhatsApp Number: {settings.TWILIO_WHATSAPP_NUMBER}")
print(f"   WhatsApp Enabled: {settings.TWILIO_WHATSAPP_ENABLED}")

print("\n🔍 Verificando servicio de WhatsApp:")
enabled = whatsapp_service.is_enabled()
print(f"   ¿WhatsApp habilitado?: {enabled}")

if enabled:
    print("\n✅ WhatsApp está configurado correctamente")
    print("\n💡 Para probar el envío, puedes:")
    print("   1. Crear una nueva reserva")
    print("   2. O usar el script de prueba manual")
else:
    print("\n❌ WhatsApp NO está habilitado")
    print("\n🔧 Verifica:")
    print("   1. Que las variables estén en .env")
    print("   2. Que el servicio se haya reiniciado")
    print("   3. Ejecuta: ./configurar_twilio.sh")
PYEOF

