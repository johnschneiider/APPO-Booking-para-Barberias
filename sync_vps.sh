#!/bin/bash
# Script para sincronizar cambios desde GitHub sin afectar configuraciones locales

set -e

echo "🔄 Sincronizando proyecto desde GitHub..."

cd /var/www/appo.com.co

# 1. Hacer backup del .env (por si acaso)
if [ -f ".env" ]; then
    cp .env .env.backup
    echo "✅ Backup de .env creado"
fi

# 2. Guardar cambios locales en stash (si hay)
git stash push -m "Cambios locales antes de pull $(date +%Y-%m-%d_%H-%M-%S)" 2>/dev/null || true

# 3. Hacer pull desde GitHub
echo "📥 Descargando cambios desde GitHub..."
git pull origin main

# 4. Restaurar el .env si se modificó
if [ -f ".env.backup" ]; then
    if ! git diff --quiet HEAD .env 2>/dev/null; then
        echo "⚠️  .env fue modificado por git, restaurando backup..."
        mv .env.backup .env
    else
        rm .env.backup
    fi
fi

# 5. Recargar variables de entorno en el servicio systemd
echo "⚙️  Actualizando servicio systemd con variables de entorno..."
# Cargar variables de forma segura
set -a
source <(grep -v '^#' .env | grep -v '^$' | grep '=' | sed 's/^/export /')
set +a

POSTGRES_DB="${POSTGRES_DB:-appo_db}"
POSTGRES_USER="${POSTGRES_USER:-appo_user}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-}"
USING_DOCKER="${USING_DOCKER:-no}"
DEBUG="${DEBUG:-False}"
SECRET_KEY="${SECRET_KEY:-}"

sudo tee /etc/systemd/system/appo.service > /dev/null <<EOF
[Unit]
Description=APPO Gunicorn daemon
After=network.target postgresql.service

[Service]
User=root
Group=root
WorkingDirectory=/var/www/appo.com.co
Environment="PATH=/var/www/appo.com.co/venv/bin"
Environment="POSTGRES_DB=$POSTGRES_DB"
Environment="POSTGRES_USER=$POSTGRES_USER"
Environment="POSTGRES_PASSWORD=$POSTGRES_PASSWORD"
Environment="POSTGRES_HOST=localhost"
Environment="POSTGRES_PORT=5432"
Environment="USING_DOCKER=$USING_DOCKER"
Environment="DEBUG=$DEBUG"
Environment="SECRET_KEY=$SECRET_KEY"
ExecStart=/var/www/appo.com.co/venv/bin/gunicorn \\
    --workers 3 \\
    --timeout 120 \\
    --bind 127.0.0.1:8888 \\
    --access-logfile /var/www/appo.com.co/logs/gunicorn-access.log \\
    --error-logfile /var/www/appo.com.co/logs/gunicorn-error.log \\
    melissa.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload

# 6. Ejecutar migraciones si hay cambios
echo "🗄️  Verificando migraciones..."
source venv/bin/activate
# Cargar variables de entorno de forma segura
set -a
source <(grep -v '^#' .env | grep -v '^$' | grep '=' | sed 's/^/export /')
set +a
python manage.py migrate --noinput

# 7. Recopilar archivos estáticos si hay cambios
echo "📁 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

# 8. Reiniciar el servicio
echo "🔄 Reiniciando servicio appo..."
sudo systemctl restart appo

# 9. Verificar que funcione
sleep 2
if systemctl is-active --quiet appo; then
    echo "✅ Servicio appo está corriendo"
    echo "✅ Sincronización completada exitosamente"
    echo ""
    echo "🌐 Aplicación disponible en: https://appo.com.co"
else
    echo "❌ Error: El servicio appo no está corriendo"
    echo "📋 Revisa los logs con: sudo journalctl -u appo -n 50"
    exit 1
fi

