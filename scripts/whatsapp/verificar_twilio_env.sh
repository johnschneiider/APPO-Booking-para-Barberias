#!/bin/bash
# Script para verificar las variables de Twilio en .env

cd /var/www/appo.com.co
source venv/bin/activate

echo "🔍 Verificando variables de Twilio en .env..."
echo ""

# Verificar si existen las variables
if [ -f .env ]; then
    echo "📋 Variables encontradas en .env:"
    grep -E "^TWILIO_" .env | sed 's/=.*/=***OCULTO***/' || echo "   ❌ No se encontraron variables TWILIO_"
    
    echo ""
    echo "📊 Estado de las variables:"
    
    TWILIO_ACCOUNT_SID=$(grep "^TWILIO_ACCOUNT_SID=" .env | cut -d'=' -f2 | xargs)
    TWILIO_AUTH_TOKEN=$(grep "^TWILIO_AUTH_TOKEN=" .env | cut -d'=' -f2 | xargs)
    TWILIO_WHATSAPP_NUMBER=$(grep "^TWILIO_WHATSAPP_NUMBER=" .env | cut -d'=' -f2 | xargs)
    
    if [ -z "$TWILIO_ACCOUNT_SID" ] || [ "$TWILIO_ACCOUNT_SID" = "" ]; then
        echo "   ❌ TWILIO_ACCOUNT_SID: NO CONFIGURADO"
    else
        echo "   ✅ TWILIO_ACCOUNT_SID: Configurado (${#TWILIO_ACCOUNT_SID} caracteres)"
    fi
    
    if [ -z "$TWILIO_AUTH_TOKEN" ] || [ "$TWILIO_AUTH_TOKEN" = "" ] || [ "$TWILIO_AUTH_TOKEN" = "tu-twilio-auth-token" ]; then
        echo "   ❌ TWILIO_AUTH_TOKEN: NO CONFIGURADO o es placeholder"
    else
        echo "   ✅ TWILIO_AUTH_TOKEN: Configurado (${#TWILIO_AUTH_TOKEN} caracteres)"
    fi
    
    if [ -z "$TWILIO_WHATSAPP_NUMBER" ]; then
        echo "   ⚠️ TWILIO_WHATSAPP_NUMBER: No configurado (usará default: +14155238886)"
    else
        echo "   ✅ TWILIO_WHATSAPP_NUMBER: $TWILIO_WHATSAPP_NUMBER"
    fi
    
    echo ""
    echo "💡 Si las variables no están configuradas, agrégalas al .env:"
    echo "   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    echo "   TWILIO_AUTH_TOKEN=tu_token_real_aqui"
    echo "   TWILIO_WHATSAPP_NUMBER=+14155238886"
else
    echo "❌ Archivo .env no encontrado"
fi

