#!/bin/bash
# Script para cambiar el puerto de Gunicorn de 8015 a 8016 en la VPS

echo "🔧 Cambiando puerto de Gunicorn de 8015 a 8016..."

# 1. Verificar qué servicios están corriendo
echo "📋 Servicios Gunicorn encontrados:"
sudo systemctl list-units --type=service | grep -E "gunicorn|appo"

# 2. Detener el servicio actual
echo "🛑 Deteniendo servicio Gunicorn..."
sudo systemctl stop gunicorn 2>/dev/null || sudo systemctl stop appo 2>/dev/null

# 3. Buscar y actualizar el archivo de servicio systemd
echo "📝 Buscando archivo de servicio..."

# Buscar archivos de servicio que puedan tener 8015
SERVICE_FILE=$(sudo find /etc/systemd/system -name "*gunicorn*.service" -o -name "*appo*.service" 2>/dev/null | head -1)

if [ -z "$SERVICE_FILE" ]; then
    echo "⚠️  No se encontró archivo de servicio. Creando uno nuevo..."
    SERVICE_FILE="/etc/systemd/system/gunicorn.service"
fi

echo "📄 Archivo de servicio: $SERVICE_FILE"

# 4. Editar el archivo de servicio (reemplazar 8015 por 8016)
if [ -f "$SERVICE_FILE" ]; then
    echo "✏️  Actualizando puerto en $SERVICE_FILE..."
    sudo sed -i 's/:8015/:8016/g' "$SERVICE_FILE"
    sudo sed -i 's/8015/8016/g' "$SERVICE_FILE"
    echo "✅ Archivo actualizado"
else
    echo "📝 Creando nuevo archivo de servicio..."
    sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Gunicorn daemon for Predicta
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/appo.com.co
Environment="PATH=/var/www/appo.com.co/venv/bin"
ExecStart=/var/www/appo.com.co/venv/bin/gunicorn \\
    --workers 3 \\
    --timeout 120 \\
    --bind 127.0.0.1:8016 \\
    melissa.wsgi:application

[Install]
WantedBy=multi-user.target
EOF
    echo "✅ Archivo creado"
fi

# 5. Actualizar configuración de Nginx
echo "📝 Actualizando configuración de Nginx..."
NGINX_CONFIG="/etc/nginx/sites-available/appo.com.co"
if [ -f "$NGINX_CONFIG" ]; then
    sudo sed -i 's/127.0.0.1:8000/127.0.0.1:8016/g' "$NGINX_CONFIG"
    sudo sed -i 's/127.0.0.1:8015/127.0.0.1:8016/g' "$NGINX_CONFIG"
    echo "✅ Nginx actualizado"
else
    echo "⚠️  No se encontró $NGINX_CONFIG, verifica manualmente"
fi

# 6. Recargar systemd
echo "🔄 Recargando systemd..."
sudo systemctl daemon-reload

# 7. Iniciar el servicio
echo "🚀 Iniciando servicio Gunicorn..."
sudo systemctl start gunicorn 2>/dev/null || sudo systemctl start appo 2>/dev/null

# 8. Habilitar el servicio para que inicie automáticamente
sudo systemctl enable gunicorn 2>/dev/null || sudo systemctl enable appo 2>/dev/null

# 9. Recargar Nginx
echo "🔄 Recargando Nginx..."
sudo nginx -t && sudo systemctl reload nginx

# 10. Verificar estado
echo "✅ Verificando estado del servicio..."
sleep 2
sudo systemctl status gunicorn 2>/dev/null || sudo systemctl status appo 2>/dev/null

echo ""
echo "🎉 ¡Completado! El puerto ahora es 8016"
echo "📊 Verifica con: sudo systemctl status gunicorn"


