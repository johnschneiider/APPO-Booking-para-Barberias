#!/bin/bash
# Script para verificar y corregir configuración de Twilio

cd /var/www/appo.com.co
source venv/bin/activate

echo "🔍 Verificando configuración de Twilio..."
echo ""

# 1. Verificar .env
echo "📋 Variables en .env:"
grep "^TWILIO_" .env || echo "   ❌ No se encontraron variables TWILIO_ en .env"

# 2. Verificar servicio systemd
echo ""
echo "📋 Variables en servicio systemd:"
sudo systemctl show appo | grep TWILIO || echo "   ❌ No se encontraron variables TWILIO_ en el servicio"

# 3. Verificar que load_dotenv esté habilitado
echo ""
echo "📋 Verificando settings.py..."
if grep -q "^load_dotenv()" melissa/settings.py; then
    echo "   ✅ load_dotenv() está habilitado"
else
    echo "   ❌ load_dotenv() NO está habilitado"
    echo "   🔧 Habilitando load_dotenv()..."
    sed -i 's|# load_dotenv()|load_dotenv()|' melissa/settings.py
    echo "   ✅ load_dotenv() habilitado"
fi

# 4. Verificar desde Django
echo ""
echo "📋 Verificando desde Django:"
python manage.py shell << 'PYEOF'
from django.conf import settings
import os

print(f"Desde os.environ:")
print(f"   TWILIO_ACCOUNT_SID: {os.environ.get('TWILIO_ACCOUNT_SID', 'NO ENCONTRADO')}")
print(f"   TWILIO_AUTH_TOKEN: {'Configurado' if os.environ.get('TWILIO_AUTH_TOKEN') else 'NO ENCONTRADO'}")

print(f"\nDesde settings:")
print(f"   TWILIO_ACCOUNT_SID: {settings.TWILIO_ACCOUNT_SID or 'NO CONFIGURADO'}")
print(f"   TWILIO_AUTH_TOKEN: {'Configurado' if settings.TWILIO_AUTH_TOKEN else 'NO CONFIGURADO'}")
print(f"   TWILIO_WHATSAPP_NUMBER: {settings.TWILIO_WHATSAPP_NUMBER}")
PYEOF

# 5. Si no están cargadas, forzar recarga
echo ""
echo "🔄 Reiniciando servicio completamente..."
sudo systemctl stop appo
sleep 3
sudo systemctl start appo
sleep 10

# 6. Verificar de nuevo
echo ""
echo "📋 Verificación final:"
python manage.py shell << 'PYEOF'
from django.conf import settings
from clientes.whatsapp_service import whatsapp_service

print(f"TWILIO_ACCOUNT_SID: {settings.TWILIO_ACCOUNT_SID[:10]}..." if settings.TWILIO_ACCOUNT_SID and len(settings.TWILIO_ACCOUNT_SID) > 10 else f"TWILIO_ACCOUNT_SID: {settings.TWILIO_ACCOUNT_SID or '❌ NO CONFIGURADO'}")
print(f"TWILIO_AUTH_TOKEN: {'✅ Configurado' if settings.TWILIO_AUTH_TOKEN and settings.TWILIO_AUTH_TOKEN != 'tu-twilio-auth-token' else '❌ NO CONFIGURADO'}")
print(f"TWILIO_WHATSAPP_NUMBER: {settings.TWILIO_WHATSAPP_NUMBER}")

enabled = whatsapp_service.is_enabled()
print(f"\n¿WhatsApp habilitado?: {enabled}")
if enabled:
    print("✅ WhatsApp está configurado correctamente")
else:
    print("❌ WhatsApp NO está habilitado")
PYEOF

