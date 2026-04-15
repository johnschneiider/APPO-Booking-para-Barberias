#!/bin/bash
# Script para desplegar cambios desde GitHub a la VPS

set -e  # Salir si hay algún error

PROJECT_DIR="/var/www/appo.com.co"
VENV_PATH="$PROJECT_DIR/venv"

echo "🚀 Iniciando despliegue de cambios..."
echo ""

# 1. Ir al directorio del proyecto
cd "$PROJECT_DIR"

# 2. Activar entorno virtual
echo "📦 Activando entorno virtual..."
source "$VENV_PATH/bin/activate"

# 3. Hacer pull de los cambios desde GitHub
echo "📥 Obteniendo cambios desde GitHub..."
git pull origin main

# 4. Instalar/actualizar dependencias si es necesario
echo "📚 Verificando dependencias..."
pip install -q -r requirements.txt

# 5. Ejecutar migraciones
echo "🗄️ Ejecutando migraciones..."
python manage.py migrate --noinput

# 6. Recopilar archivos estáticos
echo "📦 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

# 7. Reiniciar el servicio Gunicorn
echo "🔄 Reiniciando servicio Gunicorn (appo.service)..."
sudo systemctl restart appo.service

# 8. Esperar un momento para que el servicio inicie
sleep 3

# 9. Verificar estado del servicio
echo ""
echo "📊 Verificando estado del servicio..."
sudo systemctl status appo.service --no-pager -l | head -20

# 10. Verificar que el servicio esté corriendo
if sudo systemctl is-active --quiet appo.service; then
    echo ""
    echo "✅ ¡Despliegue completado exitosamente!"
    echo "🌐 El servicio está corriendo en http://appo.com.co"
else
    echo ""
    echo "❌ Error: El servicio no está corriendo"
    echo "📋 Revisa los logs con: sudo journalctl -u appo.service -n 50"
    exit 1
fi

