#!/bin/bash
# Script para actualizar el servicio systemd con las variables de Twilio

cd /var/www/appo.com.co

echo "🔧 Actualizando servicio systemd con variables de Twilio..."
echo ""

# Leer variables del .env
if [ ! -f .env ]; then
    echo "❌ Archivo .env no encontrado"
    exit 1
fi

POSTGRES_DB_VAL=$(grep "^POSTGRES_DB=" .env | cut -d'=' -f2)
POSTGRES_USER_VAL=$(grep "^POSTGRES_USER=" .env | cut -d'=' -f2)
POSTGRES_PASSWORD_VAL=$(grep "^POSTGRES_PASSWORD=" .env | cut -d'=' -f2)
USING_DOCKER_VAL=$(grep "^USING_DOCKER=" .env | cut -d'=' -f2 || echo "no")
DEBUG_VAL=$(grep "^DEBUG=" .env | cut -d'=' -f2 || echo "False")
SECRET_KEY_VAL=$(grep "^SECRET_KEY=" .env | cut -d'=' -f2)

# Leer variables de Twilio
TWILIO_ACCOUNT_SID_VAL=$(grep "^TWILIO_ACCOUNT_SID=" .env | cut -d'=' -f2 || echo "")
TWILIO_AUTH_TOKEN_VAL=$(grep "^TWILIO_AUTH_TOKEN=" .env | cut -d'=' -f2 || echo "")
TWILIO_WHATSAPP_NUMBER_VAL=$(grep "^TWILIO_WHATSAPP_NUMBER=" .env | cut -d'=' -f2 || echo "+14155238886")

echo "📋 Variables encontradas:"
echo "   TWILIO_ACCOUNT_SID: ${TWILIO_ACCOUNT_SID_VAL:0:10}..." if [ -n "$TWILIO_ACCOUNT_SID_VAL" ]; then echo "   ✅ Configurado"; else echo "   ❌ NO CONFIGURADO"; fi
echo "   TWILIO_AUTH_TOKEN: $([ -n "$TWILIO_AUTH_TOKEN_VAL" ] && echo "✅ Configurado" || echo "❌ NO CONFIGURADO")"
echo "   TWILIO_WHATSAPP_NUMBER: $TWILIO_WHATSAPP_NUMBER_VAL"
echo ""

# Actualizar servicio systemd
sudo tee /etc/systemd/system/appo.service > /dev/null <<EOF
[Unit]
Description=APPO Gunicorn daemon
After=network.target postgresql.service

[Service]
User=root
Group=root
WorkingDirectory=/var/www/appo.com.co
Environment="PATH=/var/www/appo.com.co/venv/bin"
Environment="POSTGRES_DB=$POSTGRES_DB_VAL"
Environment="POSTGRES_USER=$POSTGRES_USER_VAL"
Environment="POSTGRES_PASSWORD=$POSTGRES_PASSWORD_VAL"
Environment="POSTGRES_HOST=localhost"
Environment="POSTGRES_PORT=5432"
Environment="USING_DOCKER=$USING_DOCKER_VAL"
Environment="DEBUG=$DEBUG_VAL"
Environment="SECRET_KEY=$SECRET_KEY_VAL"
Environment="TWILIO_ACCOUNT_SID=$TWILIO_ACCOUNT_SID_VAL"
Environment="TWILIO_AUTH_TOKEN=$TWILIO_AUTH_TOKEN_VAL"
Environment="TWILIO_WHATSAPP_NUMBER=$TWILIO_WHATSAPP_NUMBER_VAL"
ExecStart=/var/www/appo.com.co/venv/bin/gunicorn \\
    --workers 3 \\
    --timeout 120 \\
    --bind 127.0.0.1:8000 \\
    --access-logfile /var/www/appo.com.co/logs/gunicorn-access.log \\
    --error-logfile /var/www/appo.com.co/logs/gunicorn-error.log \\
    melissa.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Servicio systemd actualizado"
echo ""

# Recargar y reiniciar
echo "🔄 Recargando systemd..."
sudo systemctl daemon-reload

echo "🔄 Reiniciando servicio appo..."
sudo systemctl restart appo

echo ""
echo "⏳ Esperando a que el servicio se inicie..."
sleep 10

echo ""
echo "✅ Servicio actualizado y reiniciado"
echo ""
echo "💡 Para verificar, ejecuta:"
echo "   ./probar_envio_whatsapp.sh"

